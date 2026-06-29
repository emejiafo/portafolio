#!/usr/bin/env bash

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID first}"
UPLOADS_BUCKET="${UPLOADS_BUCKET:?Set UPLOADS_BUCKET first}"
MIRROR_DELETE="${MIRROR_DELETE:-false}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-${REPO_ROOT}/data/uploads}"

if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Source directory not found: ${SOURCE_DIR}" >&2
    exit 1
fi

gcloud config set project "$PROJECT_ID" >/dev/null

args=(storage rsync "$SOURCE_DIR" "gs://${UPLOADS_BUCKET}" --recursive)
if [[ "$MIRROR_DELETE" == "true" ]]; then
    args+=(--delete-unmatched-destination-objects)
fi

gcloud "${args[@]}"

echo
echo "Uploads synced to gs://${UPLOADS_BUCKET}."