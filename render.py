#!/usr/bin/env python3
"""Render "A Room Is an EQ" -- run this file; no manim CLI needed.

Edit the settings below and press Run in your editor, or from a terminal:

    python render.py                 # rough cut: all scenes, 480p, ~1.9 min total
    python render.py --full          # full scripted length (~19 min), 1080p30
    python render.py 05 07           # only those scenes
    python render.py --scale 0.25    # any other length (fraction of ~19 min)

Each scene is written to media/eq/<SceneName>.mp4 and, when more than one
scene was rendered, joined in order into media/eq/A_Room_Is_an_EQ.mp4.
"""

from __future__ import annotations

import argparse
import importlib
import os
import pathlib
import subprocess
import sys

# ---- settings (used when you press Run with no arguments) -------------------
SCALE = 0.1          # 0.1 = rough cut (~1.9 min); 1.0 = full ~19 min
QUALITY = "draft"    # "draft" = 854x480@15, "final" = 1920x1080@30
SCENES = "all"       # "all" or a list like ["05", "07"]
# -----------------------------------------------------------------------------

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

PRESETS = {"draft": dict(pixel_width=854, pixel_height=480, frame_rate=15),
           "final": dict(pixel_width=1920, pixel_height=1080, frame_rate=30)}

CATALOGUE = {
    "00": ("roomeq.scenes.act1", "Scene00ColdOpen"),
    "01": ("roomeq.scenes.act1", "Scene01Impulse"),
    "02": ("roomeq.scenes.act1", "Scene02Mirrors"),
    "03": ("roomeq.scenes.act1", "Scene03Dont"),
    "04": ("roomeq.scenes.act2", "Scene04ImageSources"),
    "05": ("roomeq.scenes.act2", "Scene05Grid"),
    "06": ("roomeq.scenes.act3", "Scene06Pure"),
    "07": ("roomeq.scenes.act3", "Scene07EQ"),
    "08": ("roomeq.scenes.act3", "Scene08Comb"),
    "09": ("roomeq.scenes.act3", "Scene09Shower"),
    "10": ("roomeq.scenes.act4", "Scene10Bottle"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--full", action="store_true", help="scale 1.0 at 1080p30")
    ap.add_argument("--scale", type=float)
    ap.add_argument("--quality", choices=PRESETS)
    args = ap.parse_args()

    scale = 1.0 if args.full else (args.scale or SCALE)
    quality = args.quality or ("final" if args.full else QUALITY)
    # config reads this at import time, so set it before importing scenes
    os.environ["EQ_TIME_SCALE"] = str(scale)

    wanted = [s.zfill(2) for s in args.scenes] or (
        list(CATALOGUE) if SCENES == "all" else [str(s).zfill(2) for s in SCENES])
    bad = [s for s in wanted if s not in CATALOGUE]
    if bad:
        print(f"Unknown scene(s) {bad}; available: {', '.join(CATALOGUE)}")
        return 1

    from manim import tempconfig
    out_dir = ROOT / "media" / "eq"
    files = []
    for num in wanted:
        mod, cls = CATALOGUE[num]
        scene_class = getattr(importlib.import_module(mod), cls)
        with tempconfig({**PRESETS[quality], "media_dir": str(ROOT / "media" / "work"),
                         "output_file": cls}):
            scene = scene_class()
            scene.render()
            src = pathlib.Path(scene.renderer.file_writer.movie_file_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / f"{cls}.mp4"
        dst.write_bytes(src.read_bytes())
        files.append(dst)
        print(f"[{num}] {dst.relative_to(ROOT)}")

    if len(files) > 1:
        listing = out_dir / "concat.txt"
        listing.write_text("".join(f"file '{f.name}'\n" for f in files))
        joined = out_dir / "A_Room_Is_an_EQ.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(listing), "-c", "copy", str(joined)], check=True)
        listing.unlink()
        print(f"\nFull video: {joined.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
