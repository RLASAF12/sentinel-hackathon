#!/usr/bin/env bash
# Deploy Sentinel to Google Cloud Run.
#
# Prereqs: gcloud CLI authenticated, a GCP project, billing enabled.
#   gcloud auth login
#   gcloud config set project <PROJECT_ID>
#
# Usage:
#   PROJECT_ID=my-proj REGION=us-central1 ./deploy.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-sentinel}"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE}:latest"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "ERROR: set PROJECT_ID or run 'gcloud config set project <id>'." >&2
  exit 1
fi

echo "Building ${IMAGE} ..."
gcloud builds submit --tag "${IMAGE}" .

echo "Deploying ${SERVICE} to Cloud Run (${REGION}) ..."
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY:-}" \
  --port 8080

echo "Done. Health check:"
URL="$(gcloud run services describe "${SERVICE}" --region "${REGION}" --format 'value(status.url)')"
echo "  curl ${URL}/health"
