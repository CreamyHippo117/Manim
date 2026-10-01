"""Palette, layout and the timing map for "A Room Is an EQ".

Self-contained: shares no code with any other project in this repository.

Scene durations come from the script (minutes -> seconds).  ``TIME_SCALE``
shrinks every scene uniformly.  The default renders a ~1.9 minute rough cut
(10% of the scripted ~19 min); slow it down in the editor, or set
EQ_TIME_SCALE=1.0 to render at full length.
"""

from __future__ import annotations

import os

BG = "#0B0D10"
INK = "#E8E6E1"
INK_DIM = "#8C8A85"
CYAN = "#4FD8E8"
GOLD = "#F2C14E"
VIOLET = "#9B6BD6"
TEAL = "#3FBFA8"
CORAL = "#F2705F"
GHOST = "#4A4E57"
SAFE_BOTTOM = -4.0 + 8.0 * 0.12   # lowest 12% reserved for subtitles
SAFE_TOP = 4.0 * 0.9

# Roles, so a recolour touches one line.
STAMP = GOLD        # the impulse response / "the stamp" -- permanent colour
SIGNAL = CYAN       # x and y
ECHO = CORAL        # reflections, singular things
EIGEN = TEAL        # eigenvalues / the diagonal / the EQ
ODE = VIOLET        # reserved: ODE callbacks are SPOKEN in this video, never written

TIME_SCALE = float(os.environ.get("EQ_TIME_SCALE", "0.1"))

# id -> (title, seconds).  Sums to 18.75 min ("10 scenes, about 17-19 minutes").
SCENES = {
    "00": ("Cold open", 45),
    "01": ("An impulse, defined by ear", 90),
    "02": ("Walls are mirrors for sound", 90),
    "03": ("The room doesn't care", 90),
    "04": ("A room is one wall, recursively", 120),
    "05": ("The grid: rows and columns", 180),
    "06": ("The one sound a room can't change", 120),
    "07": ("A room is an EQ", 90),
    "08": ("One wall as an EQ: the comb", 90),
    "09": ("Singing in the shower", 60),
    "10": ("Stamping vs EQ, and the A/B", 150),
}


def seconds(scene_id: str) -> float:
    return SCENES[scene_id][1] * TIME_SCALE
