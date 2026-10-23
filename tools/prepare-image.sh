#!/usr/bin/env bash
# Turn a real Player screenshot into the website's JPEG + AVIF pair.
#
#   tools/prepare-image.sh <capture.png> <name> [top-crop-px]
#
# Writes assets/v1/<name>-1600.{jpg,avif} and assets/v1/<name>-800.{jpg,avif}.
# Optionally trims a black bar from the top (e.g. a window-title strip), keeps
# the frame's natural aspect ratio and never upscales. The source file is only
# read. Uses ffmpeg (Homebrew) and sips.
set -euo pipefail

[[ $# -ge 2 && $# -le 3 ]] || { echo "usage: $0 <capture.png> <name> [top-crop-px]" >&2; exit 2; }
SRC="$1"
NAME="$2"
TOP="${3:-0}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/assets/v1"

for WIDTH in 1600 800; do
  DST="$OUT/$NAME-$WIDTH.jpg"
  ffmpeg -v error -y -i "$SRC" \
    -vf "crop=iw:ih-$TOP:0:$TOP,scale='min($WIDTH,iw)':-2:flags=lanczos" \
    -q:v 4 "$DST"
  sips -s format avif -s formatOptions 60 "$DST" --out "${DST%.jpg}.avif" >/dev/null
  echo "$DST $(sips -g pixelWidth -g pixelHeight "$DST" | awk '/pixel/ {printf "%s ", $2}')"
done
