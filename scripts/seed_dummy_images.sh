#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?PROJECT_ID is required}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-microservices}"
SERVICE_NAME="${SERVICE_NAME:-example-service}"
TAG="${TAG:-v1.0.0}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/sample_services/$SERVICE_NAME"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:$TAG"

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
docker build -t "$IMAGE" "$SERVICE_DIR"
docker push "$IMAGE"

echo "Seeded $IMAGE"
echo "Wait 5+ minutes, then run the scanner to trigger a rebuild."
