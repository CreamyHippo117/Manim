#!/usr/bin/env bash
# Render the Basel film.  Run tools/verify_math.py first -- it checks every
# number the animation puts on screen against its analytic value.
set -euo pipefail

PY="${PY:-.venv/bin/python}"
MODE="${1:-draft}"

SCENES=(
  "basel/scenes/s01_mystery.py Scene01Mystery"
  "basel/scenes/s02_coaster.py Scene02Coaster"
  "basel/scenes/s03_path_independence.py Scene03PathIndependence"
  "basel/scenes/s04_accumulation.py Scene04Accumulation"
  "basel/scenes/s05_sprinkler.py Scene05Sprinkler"
  "basel/scenes/s06_residues.py Scene06Residues"
)

case "$MODE" in
  draft) FLAGS=(-ql --fps 15) ;;                      # 480p15 preview
  final) FLAGS=(-qh --fps 60 -r 1920,1080) ;;         # 1080p60
  final30) FLAGS=(-qh --fps 30 -r 1920,1080) ;;       # 1080p30
  *) echo "usage: $0 [draft|final|final30]" >&2; exit 1 ;;
esac

"$PY" tools/verify_math.py

for entry in "${SCENES[@]}"; do
  set -- $entry
  echo "=== $2 ==="
  "$PY" -m manim render "${FLAGS[@]}" "$1" "$2"
done
