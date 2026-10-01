"""Palette, layout and the timing map for "A Room Is a Matrix".

Palette matches the Basel film, but this package is self-contained: it imports
nothing from `basel/`.
Scene durations come from the script (minutes -> seconds).  ``TIME_SCALE``
shrinks every scene uniformly.  The default renders a ~2.4 minute rough cut
(10% of the scripted ~24 min); slow it down in the editor, or set
ROOM_TIME_SCALE=1.0 to render at full length.
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
ODE = VIOLET        # every ODE callback is written in this colour

TIME_SCALE = float(os.environ.get("ROOM_TIME_SCALE", "0.1"))

# id -> (title, seconds).  Sums to 23.75 min ("12 scenes, about 24 minutes").
SCENES = {
    "00": ("Cold open", 45),
    "01": ("An impulse, by ear and by integral", 90),
    "02": ("Walls are mirrors", 90),
    "03": ("Linear means \"is a matrix\"", 120),
    "04": ("A room is one wall, recursively", 120),
    "05": ("Constant diagonals: the Toeplitz grid", 180),
    "06": ("Duhamel: you've seen this matrix", 90),
    "07": ("Sines are eigenvectors", 150),
    "08": ("Change basis and the room becomes an EQ", 150),
    "09": ("One wall's eigenvalues: the comb", 90),
    "10": ("Poles: singing in the shower", 90),
    "11": ("Invert, pad, and race", 180),
}


def seconds(scene_id: str) -> float:
    return SCENES[scene_id][1] * TIME_SCALE
