#!/usr/bin/env bash
# Deploy Sentinel (live web UI) to Google Cloud Run.
#
# Serves the risk-gate web UI in LIVE mode: real Gemini 3 on Vertex AI + real
# GitLab pipeline read/cancel. Vertex auth comes from the Cloud Run service's
# service account (no key file in the image).
#
# Prereqs:
#   gcloud auth login
#   gcloud config set project sentinel-hackathon-2026
#   export GITLAB_TOKEN=glpat-...   # the sentinel-mcp PAT (not committed)
#
# Usage:
#   GITLAB_TOKEN=glpat-... ./deploy.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-sentinel}"
RUNTIME_SA="${RUNTIME_SA:-sentinel-agent@${PROJECT_ID}.iam.gserviceaccount.com}"

GITLAB_URL="${GITLAB_URL:-https://gitlab.com}"
GITLAB_PROJECT_ID="${GITLAB_PROJECT_ID:-82983615}"
SENTINEL_MODEL="${SENTINEL_MODEL:-gemini-3.1-pro-preview}"
GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "ERROR: set PROJECT_ID or run 'gcloud config set project <id>'." >&2
  exit 1
fi
if [[ -z "${GITLAB_TOKEN:-}" ]]; then
  echo "ERROR: export GITLAB_TOKEN=glpat-... before deploying." >&2
  exit 1
fi

echo "Deploying ${SERVICE} to Cloud Run (${REGION}) in ${PROJECT_ID} ..."
gcloud run deploy "${SERVICE}" \
  --source . \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "${RUNTIME_SA}" \
  --port 8080 \
  --set-env-vars "SENTINEL_DEMO=false,GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},SENTINEL_MODEL=${SENTINEL_MODEL},GITLAB_URL=${GITLAB_URL},GITLAB_PROJECT_ID=${GITLAB_PROJECT_ID},GITLAB_TOKEN=${GITLAB_TOKEN}"

URL="$(gcloud run services describe "${SERVICE}" --region "${REGION}" --format 'value(status.url)')"
echo
echo "Deployed: ${URL}"
echo "Health:   curl ${URL}/health"
