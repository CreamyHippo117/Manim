"""Single configuration block: palette, timing map, layout constants.

Everything that a retime or a recolour should touch lives here. Scene modules
import from this file and never hard-code a colour or a duration.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Visual identity
# --------------------------------------------------------------------------
BG = "#0B0D10"          # near-black background
INK = "#E8E6E1"         # off-white text
INK_DIM = "#8C8A85"     # secondary text, axes
CYAN = "#4FD8E8"        # moving points, contour paths
GOLD = "#F2C14E"        # active contributions, the chain
VIOLET = "#9B6BD6"      # potential energy
TEAL = "#3FBFA8"        # kinetic energy
CORAL = "#F2705F"       # singularities, negative residues, drains
SLATE = "#5B7FA6"       # the fluid: particles and field arrows
SLATE_DIM = "#3A506B"   # field arrows behind everything else
GHOST = "#4A4E57"       # ghosted / superseded geometry

# The flow layer must never outshine the point, the chain or the labels.
FLOW_ARROW_OPACITY = 0.32
FLOW_PARTICLE_OPACITY = 0.55

# --------------------------------------------------------------------------
# Composition
# --------------------------------------------------------------------------
FRAME_W = 14.222222222222221   # manim default 16:9 frame width at 8 units high
FRAME_H = 8.0
SAFE_MARGIN = 0.05             # 5% safe margin on every edge
SUBTITLE_RESERVE = 0.12        # lowest 12% reserved for burned-in subtitles

SAFE_TOP = FRAME_H / 2 * (1 - 2 * SAFE_MARGIN)
SAFE_BOTTOM = -FRAME_H / 2 + FRAME_H * SUBTITLE_RESERVE
SAFE_LEFT = -FRAME_W / 2 * (1 - 2 * SAFE_MARGIN)
SAFE_RIGHT = FRAME_W / 2 * (1 - 2 * SAFE_MARGIN)

TITLE_SIZE = 34
LABEL_SIZE = 24
SMALL_SIZE = 19
EQUATION_SIZE = 40

# --------------------------------------------------------------------------
# Timing
# --------------------------------------------------------------------------
TARGET_DURATION = 120.0

# Scene id -> (title, [(beat name, weight), ...]).  Weights are relative; the
# scene duration below distributes them.  A weight of 3 next to a weight of 7
# means the first beat gets three tenths of the scene, whatever the scene is
# retimed to.
SCENE_BEATS = {
    "01": ("The mystery", [
        ("terms_and_line", 2),
        ("partial_sums", 3),
        ("why_pi", 3),
    ]),
    "02": ("Coaster energy", [
        ("build_track", 3),
        ("full_ride", 7),
        ("work_meter", 3),
    ]),
    "03": ("Path independence", [
        ("split_routes", 2),
        ("race", 5),
        ("closed_loop", 3),
    ]),
    "04": ("Complex accumulation: along and across", [
        ("two_panels", 3),
        ("fence_beat", 4),
        ("one_product", 4),
        ("close_the_loop", 3),
        ("shrink", 2),
    ]),
    "05": ("A hole, a sprinkler, and 2 pi i", [
        ("puncture", 3),
        ("conjugate_flip", 3),
        ("rotation_cancel", 4),
        ("why_two_pi", 3),
        ("same_faucet", 2),
    ]),
    "06": ("Why residues survive", [
        ("dipole", 5),
        ("three_local_terms", 4),
        ("residue_theorem", 5),
    ]),
    "07": ("Design the Basel function", [
        ("requirements", 3),
        ("cotangent", 4),
        ("divide_by_z2", 4),
        ("origin_pending", 2),
    ]),
    "08": ("The residue at zero", [
        ("local_expansion", 3),
        ("divide", 4),
        ("the_drain", 4),
    ]),
    "09": ("The boundary vanishes", [
        ("square_N2", 4),
        ("expand", 4),
        ("bound_gauge", 3),
        ("limit", 2),
    ]),
    "10": ("Resolve the sum", [
        ("statement", 2),
        ("solve", 2),
        ("hold", 3),
    ]),
}

# Seconds per scene.  These ten total exactly TARGET_DURATION.
SCENE_DURATIONS = {
    "01": 8.0,
    "02": 13.0,
    "03": 10.0,
    "04": 16.0,
    "05": 15.0,
    "06": 14.0,
    "07": 13.0,
    "08": 11.0,
    "09": 13.0,
    "10": 7.0,
}

SCENE_ORDER = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]

# Per-scene overrides for a longer cut.  Populate with {"04": 40.0} and only
# scene 4 stretches; every other scene keeps its timing.  This is deliberately
# not a uniform slow-motion factor.
SCENE_DURATION_OVERRIDES: dict[str, float] = {}

# Narrator pauses are tracked separately from drawing speed so a longer cut can
# add breathing room without slowing the animation itself.
NARRATOR_PAUSE = 0.0


def scene_duration(scene_id: str) -> float:
    """Total seconds for one scene, honouring any override."""
    return float(SCENE_DURATION_OVERRIDES.get(scene_id, SCENE_DURATIONS[scene_id]))


def beat_times(scene_id: str) -> list[tuple[str, float, float]]:
    """Return [(beat_name, start, end), ...] in seconds relative to scene start."""
    _title, beats = SCENE_BEATS[scene_id]
    total_weight = sum(w for _n, w in beats)
    duration = scene_duration(scene_id)
    out: list[tuple[str, float, float]] = []
    cursor = 0.0
    for index, (name, weight) in enumerate(beats):
        if index == len(beats) - 1:
            end = duration          # absorb rounding into the last beat
        else:
            end = cursor + duration * weight / total_weight
        out.append((name, cursor, end))
        cursor = end
    return out


def scene_start(scene_id: str) -> float:
    """Absolute start time of a scene inside the assembled overview."""
    return sum(scene_duration(s) for s in SCENE_ORDER[: SCENE_ORDER.index(scene_id)])


def total_duration() -> float:
    return sum(scene_duration(s) for s in SCENE_ORDER)
