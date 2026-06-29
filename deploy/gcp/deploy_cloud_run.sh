#!/usr/bin/env bash

set -euo pipefail

if [[ "${TRACE:-false}" == "true" ]]; then
    set -x
fi

log() {
    printf "\n[%s] %s\n" "$(date +"%Y-%m-%d %H:%M:%S")" "$*"
}

require_command() {
    local cmd="$1"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Missing required command: $cmd" >&2
        exit 1
    fi
}

require_command gcloud

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID first}"
REGION="${REGION:-us-central1}"

BACKEND_SERVICE="${BACKEND_SERVICE:-portfolio-backend}"
FRONTEND_SERVICE="${FRONTEND_SERVICE:-portfolio-frontend}"
MIGRATION_JOB="${MIGRATION_JOB:-portfolio-migrate}"
SEED_JOB="${SEED_JOB:-portfolio-seed}"
RUN_SEED_DATA="${RUN_SEED_DATA:-false}"

RUNTIME_SA_NAME="${RUNTIME_SA_NAME:-portfolio-runtime}"
RUNTIME_SA_EMAIL="${RUNTIME_SA_EMAIL:-${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com}"

AR_REPO="${AR_REPO:-portfolio}"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
SKIP_IMAGE_BUILD="${SKIP_IMAGE_BUILD:-false}"

DB_INSTANCE="${DB_INSTANCE:-portfolio-pg}"
DB_VERSION="${DB_VERSION:-POSTGRES_15}"
DB_TIER="${DB_TIER:-db-f1-micro}"
DB_STORAGE_GB="${DB_STORAGE_GB:-20}"
DB_NAME="${DB_NAME:-portfolio}"
DB_USER="${DB_USER:-portfolio_app}"
DB_PASSWORD="${DB_PASSWORD:?Set DB_PASSWORD first}"

DB_URL_SECRET="${DB_URL_SECRET:-portfolio-database-url}"
DB_URL_SYNC_SECRET="${DB_URL_SYNC_SECRET:-portfolio-database-url-sync}"
APP_SECRET_KEY_SECRET="${APP_SECRET_KEY_SECRET:-portfolio-app-secret-key}"
APP_SECRET_KEY_VALUE="${APP_SECRET_KEY_VALUE:-}"

USE_GCS_MOUNT="${USE_GCS_MOUNT:-true}"
UPLOADS_BUCKET="${UPLOADS_BUCKET:-${PROJECT_ID}-portfolio-uploads}"
UPLOADS_MOUNT_PATH="${UPLOADS_MOUNT_PATH:-/app/data/uploads}"

ENABLE_ADMIN_API="${ENABLE_ADMIN_API:-false}"
BACKEND_CPU="${BACKEND_CPU:-1}"
BACKEND_MEMORY="${BACKEND_MEMORY:-1Gi}"
BACKEND_MIN_INSTANCES="${BACKEND_MIN_INSTANCES:-0}"
BACKEND_MAX_INSTANCES="${BACKEND_MAX_INSTANCES:-3}"
BACKEND_TIMEOUT_SECONDS="${BACKEND_TIMEOUT_SECONDS:-300}"
BACKEND_EXTRA_ENV_VARS="${BACKEND_EXTRA_ENV_VARS:-}"

FRONTEND_CPU="${FRONTEND_CPU:-1}"
FRONTEND_MEMORY="${FRONTEND_MEMORY:-1Gi}"
FRONTEND_MIN_INSTANCES="${FRONTEND_MIN_INSTANCES:-0}"
FRONTEND_MAX_INSTANCES="${FRONTEND_MAX_INSTANCES:-3}"
FRONTEND_TIMEOUT_SECONDS="${FRONTEND_TIMEOUT_SECONDS:-300}"
FRONTEND_API_BASE_URL="${FRONTEND_API_BASE_URL:-}"
FRONTEND_PUBLIC_API_BASE_URL="${FRONTEND_PUBLIC_API_BASE_URL:-}"
PORTFOLIO_SKY_IMAGES="${PORTFOLIO_SKY_IMAGES:-}"
FRONTEND_EXTRA_ENV_VARS="${FRONTEND_EXTRA_ENV_VARS:-}"

if [[ ! "${DB_PASSWORD}" =~ ^[A-Za-z0-9._~\-]+$ ]]; then
    echo "DB_PASSWORD must be URL-safe (letters, numbers, dot, underscore, dash, tilde)." >&2
    exit 1
fi

if [[ -z "${APP_SECRET_KEY_VALUE}" ]]; then
    require_command openssl
    APP_SECRET_KEY_VALUE="$(openssl rand -hex 32)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

BACKEND_IMAGE="${BACKEND_IMAGE:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/backend:${IMAGE_TAG}}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/frontend:${IMAGE_TAG}}"

upsert_secret() {
    local name="$1"
    local value="$2"
    if gcloud secrets describe "$name" --project "$PROJECT_ID" >/dev/null 2>&1; then
        printf "%s" "$value" | gcloud secrets versions add "$name" --data-file=- --project "$PROJECT_ID" >/dev/null
    else
        printf "%s" "$value" | gcloud secrets create "$name" --replication-policy="automatic" --data-file=- --project "$PROJECT_ID" >/dev/null
    fi
}

ensure_runtime_service_account() {
    if ! gcloud iam service-accounts describe "$RUNTIME_SA_EMAIL" --project "$PROJECT_ID" >/dev/null 2>&1; then
        gcloud iam service-accounts create "$RUNTIME_SA_NAME" \
            --display-name "Portfolio runtime" \
            --project "$PROJECT_ID"
    fi

    for role in roles/cloudsql.client roles/secretmanager.secretAccessor; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member "serviceAccount:${RUNTIME_SA_EMAIL}" \
            --role "$role" \
            --quiet >/dev/null
    done
}

ensure_artifact_registry() {
    if ! gcloud artifacts repositories describe "$AR_REPO" --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1; then
        gcloud artifacts repositories create "$AR_REPO" \
            --repository-format docker \
            --location "$REGION" \
            --description "Portfolio images" \
            --project "$PROJECT_ID"
    fi
}

ensure_cloud_sql() {
    if ! gcloud sql instances describe "$DB_INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
        gcloud sql instances create "$DB_INSTANCE" \
            --database-version "$DB_VERSION" \
            --tier "$DB_TIER" \
            --region "$REGION" \
            --storage-size "$DB_STORAGE_GB" \
            --storage-auto-increase \
            --project "$PROJECT_ID"
    fi

    if ! gcloud sql databases describe "$DB_NAME" --instance "$DB_INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
        gcloud sql databases create "$DB_NAME" \
            --instance "$DB_INSTANCE" \
            --project "$PROJECT_ID"
    fi

    if gcloud sql users list --instance "$DB_INSTANCE" --project "$PROJECT_ID" --format="value(name)" | grep -Fxq "$DB_USER"; then
        gcloud sql users set-password "$DB_USER" \
            --instance "$DB_INSTANCE" \
            --password "$DB_PASSWORD" \
            --project "$PROJECT_ID"
    else
        gcloud sql users create "$DB_USER" \
            --instance "$DB_INSTANCE" \
            --password "$DB_PASSWORD" \
            --project "$PROJECT_ID"
    fi
}

ensure_upload_bucket() {
    if [[ "$USE_GCS_MOUNT" != "true" ]]; then
        return
    fi

    if ! gcloud storage buckets describe "gs://${UPLOADS_BUCKET}" --project "$PROJECT_ID" >/dev/null 2>&1; then
        gcloud storage buckets create "gs://${UPLOADS_BUCKET}" \
            --location "$REGION" \
            --uniform-bucket-level-access \
            --project "$PROJECT_ID"
    fi

    gcloud storage buckets add-iam-policy-binding "gs://${UPLOADS_BUCKET}" \
        --member "serviceAccount:${RUNTIME_SA_EMAIL}" \
        --role "roles/storage.objectViewer" \
        --project "$PROJECT_ID" >/dev/null
}

build_images() {
    if [[ "$SKIP_IMAGE_BUILD" == "true" ]]; then
        log "Skipping image builds (SKIP_IMAGE_BUILD=true)."
        return
    fi

    gcloud builds submit "${REPO_ROOT}/backend" \
        --tag "$BACKEND_IMAGE" \
        --project "$PROJECT_ID"

    gcloud builds submit "${REPO_ROOT}/frontend" \
        --tag "$FRONTEND_IMAGE" \
        --project "$PROJECT_ID"
}

deploy_backend_service() {
    local db_connection_name="$1"

    local -a args=(
        run deploy "$BACKEND_SERVICE"
        --project "$PROJECT_ID"
        --region "$REGION"
        --platform managed
        --image "$BACKEND_IMAGE"
        --allow-unauthenticated
        --service-account "$RUNTIME_SA_EMAIL"
        --execution-environment gen2
        --port "8000"
        --cpu "$BACKEND_CPU"
        --memory "$BACKEND_MEMORY"
        --min-instances "$BACKEND_MIN_INSTANCES"
        --max-instances "$BACKEND_MAX_INSTANCES"
        --timeout "$BACKEND_TIMEOUT_SECONDS"
        --add-cloudsql-instances "$db_connection_name"
        --set-secrets "DATABASE_URL=${DB_URL_SECRET}:latest,DATABASE_URL_SYNC=${DB_URL_SYNC_SECRET}:latest,SECRET_KEY=${APP_SECRET_KEY_SECRET}:latest"
        --set-env-vars "ENVIRONMENT=production"
        --set-env-vars "DEBUG=false"
        --set-env-vars "UPLOAD_DIR=${UPLOADS_MOUNT_PATH}"
        --set-env-vars "ENABLE_ADMIN_API=${ENABLE_ADMIN_API}"
    )

    if [[ "$USE_GCS_MOUNT" == "true" ]]; then
        args+=(--add-volume "name=uploads,type=cloud-storage,bucket=${UPLOADS_BUCKET}")
        args+=(--add-volume-mount "volume=uploads,mount-path=${UPLOADS_MOUNT_PATH}")
    fi

    if [[ -n "$BACKEND_EXTRA_ENV_VARS" ]]; then
        args+=(--set-env-vars "$BACKEND_EXTRA_ENV_VARS")
    fi

    gcloud "${args[@]}"
}

run_migrations() {
    local db_connection_name="$1"

    local -a args=(
        run jobs deploy "$MIGRATION_JOB"
        --project "$PROJECT_ID"
        --region "$REGION"
        --image "$BACKEND_IMAGE"
        --service-account "$RUNTIME_SA_EMAIL"
        --execution-environment gen2
        --cpu "$BACKEND_CPU"
        --memory "$BACKEND_MEMORY"
        --tasks 1
        --max-retries 1
        --task-timeout 900
        --add-cloudsql-instances "$db_connection_name"
        --set-secrets "DATABASE_URL=${DB_URL_SECRET}:latest,DATABASE_URL_SYNC=${DB_URL_SYNC_SECRET}:latest,SECRET_KEY=${APP_SECRET_KEY_SECRET}:latest"
        --set-env-vars "ENVIRONMENT=production"
        --set-env-vars "DEBUG=false"
        --set-env-vars "UPLOAD_DIR=${UPLOADS_MOUNT_PATH}"
        --set-env-vars "ENABLE_ADMIN_API=${ENABLE_ADMIN_API}"
        --command alembic
        --args upgrade,head
    )

    if [[ -n "$BACKEND_EXTRA_ENV_VARS" ]]; then
        args+=(--set-env-vars "$BACKEND_EXTRA_ENV_VARS")
    fi

    gcloud "${args[@]}"
    gcloud run jobs execute "$MIGRATION_JOB" --project "$PROJECT_ID" --region "$REGION" --wait
}

run_seed_data() {
    local db_connection_name="$1"

    local -a args=(
        run jobs deploy "$SEED_JOB"
        --project "$PROJECT_ID"
        --region "$REGION"
        --image "$BACKEND_IMAGE"
        --service-account "$RUNTIME_SA_EMAIL"
        --execution-environment gen2
        --cpu "$BACKEND_CPU"
        --memory "$BACKEND_MEMORY"
        --tasks 1
        --max-retries 1
        --task-timeout 900
        --add-cloudsql-instances "$db_connection_name"
        --set-secrets "DATABASE_URL=${DB_URL_SECRET}:latest,DATABASE_URL_SYNC=${DB_URL_SYNC_SECRET}:latest,SECRET_KEY=${APP_SECRET_KEY_SECRET}:latest"
        --set-env-vars "ENVIRONMENT=production"
        --set-env-vars "DEBUG=false"
        --set-env-vars "UPLOAD_DIR=${UPLOADS_MOUNT_PATH}"
        --set-env-vars "ENABLE_ADMIN_API=${ENABLE_ADMIN_API}"
        --command python
        --args scripts/seed_data.py
    )

    if [[ -n "$BACKEND_EXTRA_ENV_VARS" ]]; then
        args+=(--set-env-vars "$BACKEND_EXTRA_ENV_VARS")
    fi

    gcloud "${args[@]}"
    gcloud run jobs execute "$SEED_JOB" --project "$PROJECT_ID" --region "$REGION" --wait
}

deploy_frontend_service() {
    local backend_url="$1"

    local frontend_api_base_url="$FRONTEND_API_BASE_URL"
    local frontend_public_api_base_url="$FRONTEND_PUBLIC_API_BASE_URL"

    if [[ -z "$frontend_api_base_url" ]]; then
        frontend_api_base_url="$backend_url"
    fi
    if [[ -z "$frontend_public_api_base_url" ]]; then
        frontend_public_api_base_url="$backend_url"
    fi

    local -a args=(
        run deploy "$FRONTEND_SERVICE"
        --project "$PROJECT_ID"
        --region "$REGION"
        --platform managed
        --image "$FRONTEND_IMAGE"
        --allow-unauthenticated
        --service-account "$RUNTIME_SA_EMAIL"
        --execution-environment gen2
        --port "7860"
        --cpu "$FRONTEND_CPU"
        --memory "$FRONTEND_MEMORY"
        --min-instances "$FRONTEND_MIN_INSTANCES"
        --max-instances "$FRONTEND_MAX_INSTANCES"
        --timeout "$FRONTEND_TIMEOUT_SECONDS"
        --set-env-vars "API_BASE_URL=${frontend_api_base_url}"
        --set-env-vars "PUBLIC_API_BASE_URL=${frontend_public_api_base_url}"
    )

    if [[ -n "$PORTFOLIO_SKY_IMAGES" ]]; then
        args+=(--set-env-vars "^|^PORTFOLIO_SKY_IMAGES=${PORTFOLIO_SKY_IMAGES}")
    fi

    if [[ -n "$FRONTEND_EXTRA_ENV_VARS" ]]; then
        args+=(--set-env-vars "$FRONTEND_EXTRA_ENV_VARS")
    fi

    gcloud "${args[@]}"
}

log "Setting project to ${PROJECT_ID}."
gcloud config set project "$PROJECT_ID" >/dev/null

ACTIVE_ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
if [[ -z "$ACTIVE_ACCOUNT" ]]; then
    echo "No active gcloud account found. Run: gcloud auth login" >&2
    exit 1
fi

log "Enabling required APIs."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    dns.googleapis.com \
    --project "$PROJECT_ID"

log "Ensuring runtime service account and IAM bindings."
ensure_runtime_service_account

log "Ensuring Artifact Registry repository."
ensure_artifact_registry

log "Ensuring Cloud SQL instance, database, and app user."
ensure_cloud_sql

if [[ "$USE_GCS_MOUNT" == "true" ]]; then
    log "Ensuring uploads bucket and access for runtime service account."
    ensure_upload_bucket
fi

DB_CONNECTION_NAME="$(gcloud sql instances describe "$DB_INSTANCE" --project "$PROJECT_ID" --format='value(connectionName)')"
DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${DB_CONNECTION_NAME}"
DATABASE_URL_SYNC="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${DB_CONNECTION_NAME}"

log "Upserting runtime secrets in Secret Manager."
upsert_secret "$DB_URL_SECRET" "$DATABASE_URL"
upsert_secret "$DB_URL_SYNC_SECRET" "$DATABASE_URL_SYNC"
upsert_secret "$APP_SECRET_KEY_SECRET" "$APP_SECRET_KEY_VALUE"

log "Building backend and frontend images."
build_images

log "Deploying backend Cloud Run service."
deploy_backend_service "$DB_CONNECTION_NAME"
BACKEND_URL="$(gcloud run services describe "$BACKEND_SERVICE" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')"

log "Running Alembic migrations via Cloud Run job."
run_migrations "$DB_CONNECTION_NAME"

if [[ "$RUN_SEED_DATA" == "true" ]]; then
    log "Running seed job (RUN_SEED_DATA=true)."
    run_seed_data "$DB_CONNECTION_NAME"
fi

log "Deploying frontend Cloud Run service."
deploy_frontend_service "$BACKEND_URL"
FRONTEND_URL="$(gcloud run services describe "$FRONTEND_SERVICE" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')"

cat <<EOF

Deployment complete.

Backend URL:  ${BACKEND_URL}
Frontend URL: ${FRONTEND_URL}

Next steps:
1) Sync static uploads to GCS (CV, project assets, sky images):
   ./deploy/gcp/sync_uploads_to_bucket.sh
2) Map custom domains in Cloud Run and Cloud DNS:
   ./deploy/gcp/map_custom_domain.sh

EOF