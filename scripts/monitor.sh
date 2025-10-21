#!/usr/bin/env bash
set -Eeuo pipefail

WEBHOOK="https://discord.com/api/webhooks/1430281315353231623/6nZACQqLsXqLFVQyZLX_zqcZ3UV1CcZRWXzX7l1XbxVpV3US8jWbkDCxgRgX3ObyLRE1"
CPU_T=85
RAM_T=85
DISK_T=90
ONCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cpu) CPU_T="$2"; shift 2 ;;
    --ram) RAM_T="$2"; shift 2 ;;
    --disk) DISK_T="$2"; shift 2 ;;
    --once) ONCE=true; shift ;;
    *) echo "Unknown arg $1" >&2; exit 2 ;;
  esac
done

send_alert() {
  local title="$1"
  local body="$2"
  local payload
  payload=$(printf '{"username":"DevOps Monitor","content":"%s - %s"}' "$title" "$body")
  curl -sS -H "Content-Type: application/json" -X POST -d "$payload" "$WEBHOOK"
}

check() {
  if [[ -f /proc/loadavg ]]; then
    CPU_LOAD=$(awk '{print $1}' /proc/loadavg)
    CPU_CORES=$(getconf _NPROCESSORS_ONLN)
    CPU_PCT=$(awk -v l="$CPU_LOAD" -v c="$CPU_CORES" 'BEGIN{printf("%.0f",(l/c)*100)}')
  else
    CPU_PCT=$(powershell -Command "(Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue" |
              awk '{printf("%.0f", $1)}')
  fi

  if command -v free >/dev/null 2>&1; then
    RAM_PCT=$(free | awk '/Mem:/ {printf("%.0f", $3/$2*100)}')
  else
    RAM_PCT=$(powershell -Command "(Get-Counter '\Memory\% Committed Bytes In Use').CounterSamples.CookedValue" |
              awk '{printf("%.0f", $1)}')
  fi

  if grep -qi microsoft /proc/version 2>/dev/null; then
    DISK_PCT=$(df -P / | awk 'NR==2{gsub("%","",$5); print $5}')
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    DISK_PCT=$(df -P / | awk 'NR==2{gsub("%","",$5); print $5}')
  else
    DISK_PCT=$(powershell -Command "(Get-Counter '\LogicalDisk(_Total)\% Free Space').CounterSamples.CookedValue" |
               awk '{printf("%.0f", 100 - $1)}')
  fi

  MSG="CPU: ${CPU_PCT}% | RAM: ${RAM_PCT}% | DISK: ${DISK_PCT}%"
  echo "[$(date +'%F %T')] $MSG"

  (( CPU_PCT >= CPU_T ))  && send_alert "CPU threshold exceeded" "$MSG"
  (( RAM_PCT >= RAM_T ))  && send_alert "RAM threshold exceeded" "$MSG"
  (( DISK_PCT >= DISK_T )) && send_alert "Disk threshold exceeded" "$MSG"
}

if $ONCE; then
  check
else
  while true; do
    check
    sleep 60
  done
fi
