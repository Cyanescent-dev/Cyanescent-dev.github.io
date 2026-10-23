#!/usr/bin/env bash
# Capture website screenshots from the real Cyanescent Player 1.0.0 renderer.
#
# Uses the Player's own Preset Trial Harness (native AppKit app, production
# WKWebView/WebGL renderer, deterministic music fixture) against a throwaway
# APFS clone of the frozen 1.0.0 release source. The Player repository, its
# frozen release workspaces and all signed artifacts are never written to.
#
#   tools/capture-v1-screenshots.sh [output-dir]
#
# Run only when no other Player build, acceptance test or notarisation job is
# active: the harness opens a native window and takes focus while it runs.
set -euo pipefail

PLAYER="${CYANESCENT_PLAYER_DIR:-$HOME/Documents/Projects/Cyanescent Player}"
FROZEN="$PLAYER/build/job12-free-release/frozen-source"
RELEASE_COMMIT="0c335e016c58d584e23738d4d30216a1e63ab2c2"
OUT="${1:-$HOME/Desktop/cyanescent-website-captures}"

# edition:preset-id:name — Free presets first (the site needs more Free
# examples), then the HD-quality captures still wanted for Pro.
PRESETS=(
  free:146:tie-dye-supernova
  free:147:kaleidoscopic-woodstock
  free:165:fractal-breaker
  free:174:sri-yantra-hyperspace
  free:176:toroidal-merkaba-field
  free:180:cymatic-mandala
  free:94:chaotic-butterfly-tunnels
  free:148:tesseract-unfolding
  pro:215:smuggler-run
  pro:338:fractal-lightning-cathedral
  pro:297:psilocybe-cyanescens-woodland-reverie
)

if pgrep -fl 'CyanescentPlayer' >/dev/null; then
  echo "A Cyanescent Player process is running. Quit it (and wait for any release job) first:" >&2
  pgrep -fl 'CyanescentPlayer' >&2
  exit 1
fi
[[ -x "$FROZEN/scripts/run-preset-trial.sh" ]] || { echo "Frozen release source not found: $FROZEN" >&2; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/cyanescent-capture.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
echo "Cloning frozen release source (APFS copy-on-write) into $WORK"
cp -cR "$FROZEN" "$WORK/src"
mkdir -p "$OUT"
echo "release commit $RELEASE_COMMIT; source $FROZEN" > "$OUT/PROVENANCE.txt"

for entry in "${PRESETS[@]}"; do
  IFS=: read -r edition id name <<<"$entry"
  echo "── $edition $id $name"
  "$WORK/src/scripts/run-preset-trial.sh" "$id" \
    --edition "$edition" \
    --fixture psytrance-test \
    --duration 30 \
    --capture-times 6,12,18,24,29 \
    --window-size 1600x900 \
    --output-dir "$OUT/$id-$name" || echo "   (trial reported a problem; check $OUT/$id-$name/report.md)"
done

echo
echo "Captures are in $OUT. Pick the strongest frame per preset, then for each:"
echo "  tools/prepare-image.sh <frame.png> <name>"
