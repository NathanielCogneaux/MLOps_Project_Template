#!/bin/bash

# API service deployment script (hardened)
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOLUME_NAME="airflow_shared-data"
API_CONTAINER_NAME="api-service"
API_PORT=${API_PORT:-8005}
HEALTH_ENDPOINT="http://localhost:${API_PORT}/health"

# ---------- Helpers ----------
die() { echo "ERROR: $*" >&2; exit 1; }

# ---------- Preflight ----------
cd "$PROJECT_ROOT"

[[ -f docker-compose.yaml ]] || die "docker-compose.yaml not found at project root."
[[ -f .env ]] || die ".env is missing. Create it."

# Check shared volume exists
if ! docker volume ls | grep -q "${VOLUME_NAME}"; then
    die "Error: ${VOLUME_NAME} volume not found! Run the master deploy.sh first."
fi

# ---------- Fix shared volume permissions ----------
# Use GID=0 to match Airflow and enable group access
API_UID=1000
API_GID=0
echo "Setting shared volume permissions for API access..."
docker run --rm -v "${VOLUME_NAME}:/shared-data" alpine sh -c "
  # Don't change ownership, just ensure group permissions
  chmod -R 775 /shared-data &&
  echo 'Permissions updated for shared access'
"

# ---------- Build & Up ----------
echo "Building and starting API service..."
docker-compose up -d --build --remove-orphans

echo "API deployment complete!"
echo "API available at: http://localhost:${API_PORT}"
echo "API docs at: http://localhost:${API_PORT}/docs"
