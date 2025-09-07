#!/usr/bin/env bash
# Smart Pricing – Airflow deployment
# Usage:
#   ./deploy.sh [--wipe] [--no-build] [--tail N]
# Examples:
#   ./deploy.sh                 # wipe=false, build=true, tail=50
#   ./deploy.sh --wipe          # nuke volumes & db; fresh init
#   ./deploy.sh --no-build      # reuse existing image
#   ./deploy.sh --tail 200      # tail 200 lines of logs

set -Eeuo pipefail

# ---------- Config ----------
TAIL_LINES=50
DO_BUILD=1
WIPE=0
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="docker compose"   # fallback set below if needed
AIRFLOW_WEB_URL="${AIRFLOW_WEB_URL:-http://localhost:8080}"

# ---------- Helpers ----------
die() { echo "ERROR: $*" >&2; exit 1; }
req() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

trap 'echo "Failed at line $LINENO"; exit 1' ERR

# detect docker compose vs docker-compose
if ! command -v docker >/dev/null 2>&1; then
  die "docker is not installed"
fi
if ! docker compose version >/dev/null 2>&1; then
  if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
  else
    die "Neither 'docker compose' nor 'docker-compose' is available."
  fi
fi

# ---------- Args ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wipe) WIPE=1; shift ;;
    --no-build) DO_BUILD=0; shift ;;
    --tail) TAIL_LINES="${2:-50}"; shift 2 ;;
    -h|--help)
      sed -n '1,40p' "$0"; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

# ---------- Preflight ----------
cd "$PROJECT_ROOT"

[[ -f .env ]] || die ".env is missing. Create it (based on your .env.example)."
[[ -f docker-compose.yml || -f docker-compose.yaml ]] || die "docker-compose.yml not found at project root."
[[ -f pyproject.toml ]] || die "pyproject.toml not found at project root."

echo "Using $( $COMPOSE version | head -n1 )"
echo "Project root: $PROJECT_ROOT"
echo "Airflow Web URL: $AIRFLOW_WEB_URL"
echo "WIPE volumes: $WIPE | BUILD: $DO_BUILD | LOG TAIL: $TAIL_LINES"

if ! docker volume ls | grep -q "airflow_shared-data"; then
    echo "Error: airflow_shared-data volume not found!"
    echo "Please run the master deploy.sh script from the root directory"
    exit 1
fi

# ---------- Fix volume permissions ----------
echo "Fixing volume permissions for Airflow (UID=50000, GID=0)..."
docker run --rm -v airflow_shared-data:/shared-data alpine sh -c "
  mkdir -p /shared-data/raw_data &&
  chown -R 50000:0 /shared-data &&
  chmod -R 775 /shared-data
"

# ---------- Down + optional wipe ----------
echo "Stopping stack..."
if [[ "$WIPE" -eq 1 ]]; then
  echo "Removing containers, networks, and VOLUMES (db reset)…"
  $COMPOSE down --remove-orphans --volumes
else
  $COMPOSE down --remove-orphans
fi

# ---------- Build ----------
if [[ "$DO_BUILD" -eq 1 ]]; then
  echo "Building images (this uses pyproject.toml)…"
  $COMPOSE build --pull
else
  echo "Skipping build (--no-build)"
fi

# ---------- Initialize Airflow BEFORE starting services ----------
echo "🗄️  Initializing Airflow DB & creating admin user (airflow-init)…"
$COMPOSE run --rm airflow-init

# ---------- Up ----------
echo "Starting services…"
$COMPOSE up -d

# ---------- Health check (best-effort) ----------
if command -v curl >/dev/null 2>&1; then
  echo "Waiting for Airflow webserver health…"
  ATTEMPTS=0
  until curl -fsS "${AIRFLOW_WEB_URL%/}/health" >/dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS+1))
    if [[ $ATTEMPTS -ge 60 ]]; then
      echo "Webserver health probe timed out after ~60s. Continuing anyway."
      break
    fi
    sleep 1
  done
else
  echo "curl not found; skipping health probe."
fi

# ---------- Status & Logs ----------
echo "Container status:"
$COMPOSE ps

echo "Recent logs (webserver & scheduler, last ${TAIL_LINES} lines):"
$COMPOSE logs --tail="$TAIL_LINES" airflow-webserver || true
$COMPOSE logs --tail="$TAIL_LINES" airflow-scheduler || true

# ---------- Credentials echo ----------
USER_NAME="$(grep -E '^_AIRFLOW_WWW_USER_USERNAME=' .env | cut -d '=' -f2- 2>/dev/null || true)"
USER_PASS="$(grep -E '^_AIRFLOW_WWW_USER_PASSWORD=' .env | cut -d '=' -f2- 2>/dev/null || true)"

echo "Done. Airflow UI → ${AIRFLOW_WEB_URL}"

if [[ -n "$USER_NAME" && -n "$USER_PASS" ]]; then
    echo "Username: ${USER_NAME}"
    echo "Password: ${USER_PASS}"
else
    echo "Credentials not found in .env file"
fi

# ---------- Post-hints ----------
echo "Tips:"
echo "  • First run? Use: ./deploy.sh --wipe             # resets volumes & DB"
echo "  • Faster rebuilds after code changes: keep Dockerfile layer order (pyproject → install → copy code)"
echo "  • Tail live logs:   $COMPOSE logs -f airflow-scheduler"