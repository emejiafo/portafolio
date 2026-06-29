#!/usr/bin/env bash

set -euo pipefail

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

FRONTEND_SERVICE="${FRONTEND_SERVICE:-portfolio-frontend}"
BACKEND_SERVICE="${BACKEND_SERVICE:-portfolio-backend}"

FRONTEND_DOMAIN="${FRONTEND_DOMAIN:-}"
BACKEND_DOMAIN="${BACKEND_DOMAIN:-}"

ROOT_DOMAIN="${ROOT_DOMAIN:-}"
DNS_ZONE="${DNS_ZONE:-}"

if [[ -z "$FRONTEND_DOMAIN" && -z "$BACKEND_DOMAIN" ]]; then
    echo "Set FRONTEND_DOMAIN and/or BACKEND_DOMAIN first." >&2
    exit 1
fi

ensure_dns_zone() {
    if [[ -z "$ROOT_DOMAIN" || -z "$DNS_ZONE" ]]; then
        return
    fi

    if ! gcloud dns managed-zones describe "$DNS_ZONE" --project "$PROJECT_ID" >/dev/null 2>&1; then
        gcloud dns managed-zones create "$DNS_ZONE" \
            --dns-name "${ROOT_DOMAIN%.}." \
            --description "Managed zone for portfolio domains" \
            --project "$PROJECT_ID"
    fi
}

ensure_domain_mapping() {
    local service="$1"
    local domain="$2"

    if gcloud beta run domain-mappings describe \
        --project "$PROJECT_ID" \
        --region "$REGION" \
        --domain "$domain" >/dev/null 2>&1; then
        log "Domain mapping already exists: ${domain}"
        return
    fi

    gcloud beta run domain-mappings create \
        --project "$PROJECT_ID" \
        --region "$REGION" \
        --service "$service" \
        --domain "$domain"
}

print_mapping_status() {
    local domain="$1"
    echo
    echo "### ${domain}"
    gcloud beta run domain-mappings describe \
        --project "$PROJECT_ID" \
        --region "$REGION" \
        --domain "$domain" \
        --format="yaml(status.conditions,status.resourceRecords)"
}

print_cloud_dns_commands() {
    local domain="$1"

    if [[ -z "$DNS_ZONE" ]]; then
        return
    fi

    local records
    records="$(gcloud beta run domain-mappings describe \
        --project "$PROJECT_ID" \
        --region "$REGION" \
        --domain "$domain" \
        --format="value(status.resourceRecords[].type,status.resourceRecords[].name,status.resourceRecords[].rrdata)")"

    if [[ -z "$records" ]]; then
        return
    fi

    echo
    echo "Cloud DNS commands for ${domain} (zone: ${DNS_ZONE}):"
    while read -r rec_type rec_name rec_data; do
        [[ -z "$rec_type" ]] && continue
        echo "gcloud dns record-sets create \"${rec_data}\" --name=\"${rec_name}\" --type=\"${rec_type}\" --ttl=300 --zone=\"${DNS_ZONE}\" --project=\"${PROJECT_ID}\""
    done <<< "$records"
}

log "Setting project to ${PROJECT_ID}."
gcloud config set project "$PROJECT_ID" >/dev/null

log "Enabling required APIs."
gcloud services enable run.googleapis.com dns.googleapis.com --project "$PROJECT_ID"

if [[ -n "$ROOT_DOMAIN" && -n "$DNS_ZONE" ]]; then
    log "Ensuring Cloud DNS managed zone ${DNS_ZONE}."
    ensure_dns_zone
fi

echo
echo "Before proceeding, make sure your domain is verified for this project in Google Search Console."

if [[ -n "$FRONTEND_DOMAIN" ]]; then
    log "Ensuring frontend mapping: ${FRONTEND_DOMAIN} -> ${FRONTEND_SERVICE}."
    ensure_domain_mapping "$FRONTEND_SERVICE" "$FRONTEND_DOMAIN"
fi

if [[ -n "$BACKEND_DOMAIN" ]]; then
    log "Ensuring backend mapping: ${BACKEND_DOMAIN} -> ${BACKEND_SERVICE}."
    ensure_domain_mapping "$BACKEND_SERVICE" "$BACKEND_DOMAIN"
fi

echo
echo "Domain mapping status and DNS records:"

if [[ -n "$FRONTEND_DOMAIN" ]]; then
    print_mapping_status "$FRONTEND_DOMAIN"
    print_cloud_dns_commands "$FRONTEND_DOMAIN"
fi

if [[ -n "$BACKEND_DOMAIN" ]]; then
    print_mapping_status "$BACKEND_DOMAIN"
    print_cloud_dns_commands "$BACKEND_DOMAIN"
fi

cat <<EOF

When DNS is in place, certificates are provisioned automatically by Cloud Run.
Provisioning can take several minutes.

EOF