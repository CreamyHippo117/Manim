#!/usr/bin/env python3
"""Render the Basel film.  Run this file directly -- no manim CLI needed.

In Wing IDE: open this file and press Run (the green arrow), or use
"Debug/Run Current File".  Nothing needs to be typed at a terminal, and the
`manim` command does not need to be on your PATH -- this imports manim as a
library and drives the renderer itself.

Edit the two settings just below to choose what gets rendered and at what
quality, then Run again.

This file must sit next to the `basel/` folder (that is, in the repository
root).  It puts its own folder on sys.path, so it does not matter what Wing
has set as the working directory.
"""

from __future__ import annotations

import pathlib
import sys
import time

# ---------------------------------------------------------------------------
# Settings -- edit these, then press Run
# ---------------------------------------------------------------------------

QUALITY = "draft"      # "draft" = 854x480 @ 15 fps,  "final" = 1920x1080 @ 60 fps

SCENES = "all"         # "all", or a list of scene numbers, e.g. ["04", "05"]

VERIFY_FIRST = True    # run the 75 maths checks before rendering

OPEN_WHEN_DONE = False # True asks your OS to open each finished video

# ---------------------------------------------------------------------------


HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Scene number -> (module path, class name).  Scenes 07-10 are not written yet.
CATALOGUE = {
    "01": ("basel.scenes.s01_mystery", "Scene01Mystery"),
    "02": ("basel.scenes.s02_coaster", "Scene02Coaster"),
    "03": ("basel.scenes.s03_path_independence", "Scene03PathIndependence"),
    "04": ("basel.scenes.s04_accumulation", "Scene04Accumulation"),
    "05": ("basel.scenes.s05_sprinkler", "Scene05Sprinkler"),
    "06": ("basel.scenes.s06_residues", "Scene06Residues"),
}

PRESETS = {
    "draft": {"pixel_width": 854, "pixel_height": 480, "frame_rate": 15},
    "final": {"pixel_width": 1920, "pixel_height": 1080, "frame_rate": 60},
    "final30": {"pixel_width": 1920, "pixel_height": 1080, "frame_rate": 30},
}

INSTALL_HELP = """
manim is not installed for the interpreter Wing is using:

    {exe}

Install it for THAT interpreter (the path matters -- installing for a
different Python is the usual reason this keeps failing):

    "{exe}" -m pip install manim

On Debian or Ubuntu, manim needs some system libraries first, and it must go
into a virtual environment rather than the system Python:

    sudo apt-get install -y build-essential pkg-config libcairo2-dev \\
        libpango1.0-dev ffmpeg texlive texlive-latex-extra dvisvgm
    python3 -m venv .venv
    .venv/bin/pip install -U pip setuptools wheel
    .venv/bin/pip install manim

Then point Wing at that interpreter:
    Project -> Project Properties -> Python Executable -> Custom
    and choose  {venv}
"""


def preflight() -> bool:
    """Check the things that actually go wrong, and say so in plain words."""
    ok = True

    try:
        import manim  # noqa: F401
    except ImportError:
        print(INSTALL_HELP.format(exe=sys.executable,
                                  venv=HERE / ".venv" / "bin" / "python"))
        return False

    import shutil
    if shutil.which("ffmpeg") is None:
        print("! ffmpeg was not found on PATH. manim needs it to write videos.")
        print("  Debian/Ubuntu: sudo apt-get install ffmpeg")
        print("  macOS:         brew install ffmpeg")
        print("  Windows:       https://ffmpeg.org/download.html")
        ok = False

    if shutil.which("latex") is None:
        print("! latex was not found on PATH. The equations are typeset with")
        print("  LaTeX, so rendering will fail without a TeX distribution.")
        print("  Debian/Ubuntu: sudo apt-get install texlive texlive-latex-extra dvisvgm")
        print("  macOS:         brew install --cask mactex-no-gui")
        print("  Windows:       https://miktex.org/download")
        ok = False

    return ok


def chosen_scenes():
    if SCENES == "all":
        return list(CATALOGUE)
    wanted = [str(s).zfill(2) for s in SCENES]
    unknown = [s for s in wanted if s not in CATALOGUE]
    if unknown:
        print(f"! Unknown scene(s): {', '.join(unknown)}")
        print(f"  Available: {', '.join(CATALOGUE)}  (07-10 are not written yet)")
    return [s for s in wanted if s in CATALOGUE]


def main() -> int:
    print(f"Python:  {sys.executable}")
    print(f"Folder:  {HERE}")

    if not (HERE / "basel").is_dir():
        print("\n! No 'basel' folder next to this file.")
        print("  Put render.py in the repository root, beside basel/ and tools/.")
        return 1

    if not preflight():
        return 1

    import manim
    from manim import config, tempconfig
    print(f"manim:   {manim.__version__}")

    if QUALITY not in PRESETS:
        print(f"\n! QUALITY must be one of: {', '.join(PRESETS)}")
        return 1

    if VERIFY_FIRST:
        print("\nChecking the maths before rendering...")
        import subprocess
        result = subprocess.run([sys.executable, str(HERE / "tools" / "verify_math.py")],
                                capture_output=True, text=True)
        tail = [line for line in result.stdout.splitlines() if line.strip()][-1:]
        print("  " + (tail[0] if tail else "(no output)"))
        if result.returncode != 0:
            print("\n! Maths checks FAILED -- not rendering. Full output:\n")
            print(result.stdout[-4000:])
            return 1

    scenes = chosen_scenes()
    if not scenes:
        return 1

    preset = PRESETS[QUALITY]
    print(f"\nRendering {len(scenes)} scene(s) at "
          f"{preset['pixel_width']}x{preset['pixel_height']} @ "
          f"{preset['frame_rate']} fps\n")

    import importlib
    produced = []
    for number in scenes:
        module_path, class_name = CATALOGUE[number]
        module = importlib.import_module(module_path)
        scene_class = getattr(module, class_name)

        started = time.time()
        print(f"  [{number}] {class_name} ...", end="", flush=True)
        # A fresh config per scene, restored afterwards by the context manager.
        with tempconfig({**preset,
                         "media_dir": str(HERE / "media"),
                         "preview": OPEN_WHEN_DONE,
                         "output_file": class_name}):
            scene = scene_class()
            scene.render()
            output = pathlib.Path(scene.renderer.file_writer.movie_file_path)
        produced.append(output)
        print(f" done in {time.time() - started:.1f}s")

    print("\nWrote:")
    for path in produced:
        try:
            shown = path.relative_to(HERE)
        except ValueError:
            shown = path
        print(f"  {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
