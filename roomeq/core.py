"""Scene base class, pacing, and the shared drawing helpers."""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Axes, FadeIn, FadeOut, Line,
    MathTex, Rectangle, Scene, Square, Text, VGroup, config,
)

from .config import (
    BG, ECHO, EIGEN, GHOST, INK, INK_DIM, ODE, SAFE_BOTTOM, SAFE_TOP, SIGNAL,
    STAMP, seconds,
)


class RoomScene(Scene):
    """Applies the palette; snaps every duration to whole frames so the file
    length equals the scripted length at any frame rate."""

    scene_id = "00"

    def setup(self):
        self.camera.background_color = BG
        self.pacer = Pacer(self, seconds(self.scene_id))

    def _frames(self, d, minimum):
        fps = float(config.frame_rate)
        return max(minimum, int(round(float(d) * fps))) / fps

    def play(self, *a, **k):
        if k.get("run_time") is not None:
            k["run_time"] = self._frames(k["run_time"], 1)
        return super().play(*a, **k)

    def wait(self, duration=1.0, *a, **k):
        d = self._frames(duration, 0)
        return super().wait(d, *a, **k) if d > 0 else None


class Pacer:
    """Cumulative-fraction beats: ``beat(0.25, fn)`` runs ``fn(seconds)`` and
    pads so the beat ends at 25% of the scene, whatever fn did.  Drift cannot
    accumulate because each beat is pinned to an absolute time."""

    def __init__(self, scene, total):
        self.scene, self.total, self.t0 = scene, total, scene.renderer.time

    def now(self):
        return self.scene.renderer.time - self.t0

    def beat(self, end_frac, fn=None):
        end = self.total * end_frac
        if fn is not None:
            fn(max(end - self.now(), 0.0))
        self.scene.wait(max(end - self.now(), 0.0))

    def finish(self):
        self.scene.wait(max(self.total - self.now(), 0.0))


def run(scene_cls):
    """Decorator-free helper: build() then pad to the scripted length."""
    return scene_cls


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------
def head(text, size=34):
    return Text(text, font_size=size, color=INK).to_edge(UP, buff=0.35)


def say(text, size=22, color=INK_DIM):
    """Narration line above the reserved subtitle band."""
    return Text(text, font_size=size, color=color).move_to([0, SAFE_BOTTOM + 0.3, 0])


def tex(*parts, size=40, color=INK, **kw):
    return MathTex(*parts, font_size=size, color=color, **kw)


def ode_note(text, size=24):
    """An ODE callback, always written in the ODE colour."""
    return MathTex(text, font_size=size, color=ODE)


# ---------------------------------------------------------------------------
# Signals and axes
# ---------------------------------------------------------------------------
def stem_plot(values, width=6.0, height=1.8, color=SIGNAL, ymax=None, baseline=True):
    """Discrete signal as stems; returns (group, stems list, anchor line)."""
    n = len(values)
    ymax = ymax or max(1e-9, float(np.max(np.abs(values))))
    xs = np.linspace(-width / 2, width / 2, n)
    base = Line([-width / 2 - 0.2, 0, 0], [width / 2 + 0.2, 0, 0],
                stroke_width=1.5, color=INK_DIM)
    stems = []
    for x, v in zip(xs, values):
        top = v / ymax * height / 2
        s = Line([x, 0, 0], [x, top, 0], stroke_width=5, color=color)
        stems.append(s)
    g = VGroup(base if baseline else VGroup(), *stems)
    return g, stems


def matrix_grid(M, cell=0.42, cmap=None, stroke=0.6):
    """Draw an array as squares whose fill opacity encodes |value|.
    Returns a VGroup indexed [row*ncols+col]."""
    M = np.asarray(M, dtype=complex)
    r, c = M.shape
    mx = max(1e-9, np.abs(M).max())
    out = VGroup()
    for i in range(r):
        for j in range(c):
            v = M[i, j]
            s = Square(cell, stroke_width=stroke, stroke_color=INK_DIM,
                       stroke_opacity=0.5)
            op = float(abs(v) / mx)
            s.set_fill(cmap or STAMP, opacity=0.9 * op if op > 1e-9 else 0.0)
            s.move_to([(j - (c - 1) / 2) * cell, -(i - (r - 1) / 2) * cell, 0])
            out.add(s)
    out.n_rows, out.n_cols = r, c
    return out


def cell(grid, i, j):
    return grid[i * grid.n_cols + j]


def column_vector(n, cell_size=0.42, color=SIGNAL, lit=None):
    g = VGroup()
    for i in range(n):
        s = Square(cell_size, stroke_width=0.8, stroke_color=INK_DIM)
        s.set_fill(color, opacity=0.9 if (lit is not None and i == lit) else 0.0)
        s.move_to([0, -(i - (n - 1) / 2) * cell_size, 0])
        g.add(s)
    return g


def poly(points, color, width=3.5):
    from manim import VMobject
    m = VMobject(color=color, stroke_width=width)
    m.set_points_as_corners(np.asarray(points))
    return m


def curve_on(axes, xs, ys, color, width=3.5):
    return poly([axes.c2p(x, y) for x, y in zip(xs, ys)], color, width)


def sliders(heights, width=5.0, height=1.8, color=EIGEN, knobs=False):
    """A graphic EQ: one slider per entry, height in 0..1.  With ``knobs`` each
    slider gets a small phase dial beneath it.  Returns (group, dots)."""
    from manim import Circle, Dot
    n = len(heights)
    xs = np.linspace(-width / 2, width / 2, n)
    g, dots = VGroup(), []
    for x, h in zip(xs, heights):
        g.add(Line([x, 0, 0], [x, height, 0], stroke_width=2, color=GHOST))
        d = Dot([x, h * height, 0], radius=0.07, color=color)
        dots.append(d)
        g.add(d)
        if knobs:
            g.add(Circle(radius=0.09, stroke_width=1.5, color=INK_DIM).move_to([x, -0.35, 0]))
    return g, dots
