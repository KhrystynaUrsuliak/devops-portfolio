#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="${1:-}" 
BACKUP_DIR="${2:-}"

# SOURCE_DIR="/c/Users/User/Documents/university-labs/devops/devops-portfolio/source"
# BACKUP_DIR="/c/Users/User/Documents/university-labs/devops/devops-portfolio/backup"

RETAIN=5
LOG_FILE="backup.log"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --retain) RETAIN="${2}"; shift 2 ;;
    --log) LOG_FILE="${2}"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "${SOURCE_DIR}" || -z "${BACKUP_DIR}" ]]; then
  echo "Usage: $0 <source_dir> <backup_dir> [--retain N] [--log file]" >&2
  exit 2
fi

mkdir -p "${BACKUP_DIR}"
LOG_FILE="${BACKUP_DIR%/}/${LOG_FILE}"
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
ARCHIVE="${BACKUP_DIR%/}/backup_${TIMESTAMP}.tar.gz"

log(){ echo "[$(date +'%F %T')] $*" | tee -a "$LOG_FILE" ;}

trap 'log "Error on line $LINENO"; exit 1' ERR

log "Start backup: ${SOURCE_DIR} → ${ARCHIVE}"
tar -czf "${ARCHIVE}" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" 2>>"$LOG_FILE"
log "Created: ${ARCHIVE}"

mapfile -t ALL < <(ls -1t "${BACKUP_DIR}"/backup_*.tar.gz 2>/dev/null || true)
COUNT="${#ALL[@]}"
if (( COUNT > RETAIN )); then
  TO_DELETE=("${ALL[@]:RETAIN}")
  log "Deleting old backups (keep ${RETAIN}):"
  printf '%s\n' "${TO_DELETE[@]}" | tee -a "$LOG_FILE"
  rm -f -- "${TO_DELETE[@]}"
fi

log "Done"
