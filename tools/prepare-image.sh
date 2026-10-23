#!/usr/bin/env bash
# Turn a real Player capture into the website's 16:9 JPEG + AVIF pair.
#
#   tools/prepare-image.sh <capture.png> <name>
#
# Writes assets/v1/<name>-1600.{jpg,avif} and assets/v1/<name>-800.{jpg,avif}.
# Centre-crops to 16:9 and never upscales. Uses ffmpeg (Homebrew) and sips.
set -euo pipefail

[[ $# -eq 2 ]] || { echo "usage: $0 <capture.png> <name>" >&2; exit 2; }
SRC="$1"
NAME="$2"
OUT="$(cd "$(dirname "$0")/.." && pwd)/assets/v1"

for WIDTH in 1600 800; do
  DST="$OUT/$NAME-$WIDTH.jpg"
  ffmpeg -v error -y -i "$SRC" \
    -vf "crop='min(iw,ih*16/9)':'min(ih,iw*9/16)',scale='min($WIDTH,iw)':-2:flags=lanczos" \
    -q:v 4 "$DST"
  sips -s format avif -s formatOptions 60 "$DST" --out "${DST%.jpg}.avif" >/dev/null
  echo "$DST ($(sips -g pixelWidth "$DST" | awk '/pixelWidth/ {print $2}')px wide)"
done
