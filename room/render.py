#!/usr/bin/env python3
"""Render "A Room Is a Matrix".  Run from the repo root or press Run in an IDE.

    python room/render.py              # all scenes, 480p15, ~2.4 min rough cut
    python room/render.py 05 07        # just those scenes
    ROOM_TIME_SCALE=1.0 python room/render.py   # full ~24 min length
"""

from __future__ import annotations

import importlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

QUALITY = os.environ.get("ROOM_QUALITY", "draft")  # draft | final
PRESETS = {"draft": dict(pixel_width=854, pixel_height=480, frame_rate=15),
           "final": dict(pixel_width=1920, pixel_height=1080, frame_rate=30)}

CATALOGUE = {
    "00": ("room.scenes.act1", "Scene00ColdOpen"),
    "01": ("room.scenes.act1", "Scene01Impulse"),
    "02": ("room.scenes.act1", "Scene02Mirrors"),
    "03": ("room.scenes.act1", "Scene03Linear"),
    "04": ("room.scenes.act2", "Scene04ImageSources"),
    "05": ("room.scenes.act2", "Scene05Toeplitz"),
    "06": ("room.scenes.act2", "Scene06Duhamel"),
    "07": ("room.scenes.act3", "Scene07Eigenvectors"),
    "08": ("room.scenes.act3", "Scene08ChangeBasis"),
    "09": ("room.scenes.act3", "Scene09Comb"),
    "10": ("room.scenes.act3", "Scene10Poles"),
    "11": ("room.scenes.act4", "Scene11InvertPadRace"),
}


def main(argv):
    from manim import tempconfig
    wanted = [a.zfill(2) for a in argv] or list(CATALOGUE)
    for num in wanted:
        mod, cls = CATALOGUE[num]
        scene_class = getattr(importlib.import_module(mod), cls)
        with tempconfig({**PRESETS[QUALITY], "media_dir": str(ROOT / "media" / "room"),
                         "output_file": cls}):
            scene_class().render()
        print(f"[{num}] {cls} done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
