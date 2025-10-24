#!/bin/bash
set -e

# Ir a la raíz del proyecto (directorio padre de 'cron')
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cd "$ROOT_DIR"
log "Ejecutando pipeline desde $ROOT_DIR"
log "Ejecutando uploader"
docker compose run --rm processing
log "Pipeline completado correctamente"
