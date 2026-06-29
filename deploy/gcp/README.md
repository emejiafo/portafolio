# GCP Deployment Guide

This guide deploys the portfolio stack fully on Google Cloud with managed services:

- Cloud Run for frontend and backend
- Cloud SQL for PostgreSQL
- Secret Manager for application secrets
- Cloud Storage for CV and uploaded assets
- Cloud DNS and Cloud Run domain mappings for custom domains

## Target Architecture

- Frontend service: Gradio app on Cloud Run
- Backend service: FastAPI app on Cloud Run
- Database: Cloud SQL PostgreSQL instance
- Assets: Cloud Storage bucket mounted at /app/data/uploads in backend
- Custom domains (recommended):
  - Frontend: portfolio.example.com
  - Backend API: api.portfolio.example.com

## Prerequisites

1. Install and authenticate gcloud CLI.
2. Enable billing for the target project.
3. Verify domain ownership in Google Search Console for the target project.
4. If you want DNS managed entirely in GCP, delegate your domain to a Cloud DNS zone.

## Quick Start

1. Copy environment template and update values.

   cp deploy/gcp/env.example deploy/gcp/env.sh
   nano deploy/gcp/env.sh

2. Load variables.

   source deploy/gcp/env.sh

3. Deploy Cloud Run services, Cloud SQL, secrets, and migration job.

   ./deploy/gcp/deploy_cloud_run.sh

4. Sync static files (CV, project images, sky images) into Cloud Storage.

   ./deploy/gcp/sync_uploads_to_bucket.sh

5. Map custom domains and print DNS records.

   ./deploy/gcp/map_custom_domain.sh

6. Once domain DNS and certificates are active, point frontend API env vars at backend custom domain.

   export FRONTEND_API_BASE_URL="https://${BACKEND_DOMAIN}"
   export FRONTEND_PUBLIC_API_BASE_URL="https://${BACKEND_DOMAIN}"
   export SKIP_IMAGE_BUILD="true"
   ./deploy/gcp/deploy_cloud_run.sh

## Cost Control Defaults

The template defaults are tuned for lower cost:

- Cloud Run min instances: 0 for frontend and backend
- Cloud SQL tier: db-f1-micro
- Cloud Run max instances: 3

These defaults are suitable for low traffic and development workloads. Increase resources when latency or throughput requires it.

## Security Note

This repository now supports disabling administrative API routes by setting:

- ENABLE_ADMIN_API=false

The deploy template sets this to false, so only public endpoints remain exposed on the internet by default.

## Common Operations

Run migrations after schema changes:

gcloud run jobs execute "${MIGRATION_JOB}" --region "${REGION}" --project "${PROJECT_ID}" --wait

Run seed data again:

gcloud run jobs execute "${SEED_JOB}" --region "${REGION}" --project "${PROJECT_ID}" --wait

View service URLs:

gcloud run services describe "${FRONTEND_SERVICE}" --region "${REGION}" --project "${PROJECT_ID}" --format='value(status.url)'
gcloud run services describe "${BACKEND_SERVICE}" --region "${REGION}" --project "${PROJECT_ID}" --format='value(status.url)'

## Cleanup

Delete services and jobs:

gcloud run services delete "${FRONTEND_SERVICE}" "${BACKEND_SERVICE}" --region "${REGION}" --project "${PROJECT_ID}"
gcloud run jobs delete "${MIGRATION_JOB}" "${SEED_JOB}" --region "${REGION}" --project "${PROJECT_ID}"

Delete Cloud SQL instance:

gcloud sql instances delete "${DB_INSTANCE}" --project "${PROJECT_ID}"

Delete uploads bucket:

gcloud storage rm --recursive "gs://${UPLOADS_BUCKET}"
gcloud storage buckets delete "gs://${UPLOADS_BUCKET}"