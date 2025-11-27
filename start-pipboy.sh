#!/usr/bin/env bash
set -euo pipefail

LOG="/home/borys/pipboy/pipboy.log"
APP_DIR="/home/borys/pipboy"
PY="/usr/bin/python3"

SPI_DEV="/dev/spidev0.0"   # если у тебя другой — поменяй на spidev0.1 и т.п.

echo "[$(date)] start-pipboy.sh: boot start" >> "$LOG"

# Ждём появление SPI-девайса
for i in $(seq 1 60); do
  if [ -e "$SPI_DEV" ]; then
    echo "[$(date)] SPI device $SPI_DEV found" >> "$LOG"
    break
  fi
  echo "[$(date)] waiting for SPI ($SPI_DEV) ... $i" >> "$LOG"
  sleep 1
done

# Если так и не появился — пишем и выходим
if [ ! -e "$SPI_DEV" ]; then
  echo "[$(date)] ERROR: SPI device not found after 60s, exiting" >> "$LOG"
  exit 1
fi

# На всякий случай проверим права (иногда SPI появляется, но ещё без прав)
for i in $(seq 1 20); do
  if [ -r "$SPI_DEV" ] && [ -w "$SPI_DEV" ]; then
    echo "[$(date)] SPI device has rw access" >> "$LOG"
    break
  fi
  echo "[$(date)] waiting for rw permissions on SPI ... $i" >> "$LOG"
  sleep 1
done

cd "$APP_DIR"
echo "[$(date)] launching pipboy..." >> "$LOG"
exec "$PY" main.py >> "$LOG" 2>&1
