"""Act II -- Stacking copies (scenes 4-5).  No ODE text on screen."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Brace, Circle, Create, Dot, FadeIn, FadeOut, Line,
    Rectangle, Text, Transform, TransformMatchingTex, VGroup, ValueTracker, Write,
    always_redraw,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from roomeq.config import CORAL, ECHO, EIGEN, GHOST, GOLD, INK, INK_DIM, SIGNAL, STAMP  # noqa: E402
from roomeq.core import RoomScene, cell, curve_on, head, matrix_grid, say, tex  # noqa: E402
from roomeq import mathcore as mc  # noqa: E402


def lbl(text, size=20, color=INK_DIM):
    return Text(text, font_size=size, color=color)


class Scene04ImageSources(RoomScene):
    scene_id = "04"

    def construct(self):
        p = self.pacer
        self.add(head("A room is one wall, recursively"))
        sc = 0.34
        ox, oy = -3.6, -1.9
        rooms = VGroup(*[Rectangle(width=6 * sc, height=4 * sc, stroke_width=0.8, stroke_color=GHOST
                                   ).move_to([(3 + 6 * i) * sc + ox, (2 + 4 * j) * sc + oy, 0])
                         for i in range(-3, 4) for j in range(-3, 4)])
        centre = np.array([3 * sc + ox, 2 * sc + oy, 0])
        pts = mc.image_sources(order=3)
        dots = VGroup(*[Dot([x * sc + ox, y * sc + oy, 0], radius=0.055,
                            color=STAMP if o == 0 else ECHO).set_opacity(max(0.3, 1 - 0.14 * o))
                        for x, y, o in pts])
        walls_lbl = lbl("add walls one at a time: each mirrors all the existing mirrors", 20)
        walls_lbl.to_edge(DOWN, buff=1.0)
        p.beat(0.3, lambda rt: (self.play(FadeIn(rooms, lag_ratio=0.03), FadeIn(walls_lbl), run_time=rt / 2),
                                self.play(FadeIn(dots, lag_ratio=0.02), run_time=rt / 3)))
        # a circle grows at the speed of sound; each swallowed mirrored room is a new echo
        r = ValueTracker(0.1)
        circ = always_redraw(lambda: Circle(radius=r.get_value(), color=SIGNAL, stroke_width=3
                                            ).move_to(centre))
        grow_l = lbl("a growing circle: each new mirrored room it swallows is a new echo", 20, SIGNAL
                     ).to_edge(DOWN, buff=1.0)
        # spike train on the right
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 1], x_length=5, y_length=1.8,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(RIGHT * 3.6 + UP * 0.8)
        def spikes_upto(rad):
            out = VGroup()
            for x, y, o in pts:
                d = np.hypot(x * sc + ox - centre[0], y * sc + oy - centre[1])
                if d <= rad:
                    t = d / 4.2
                    out.add(Line(ax.c2p(t, 0), ax.c2p(t, np.exp(-2.2 * t) * 0.9 + 0.05),
                                 stroke_width=3, color=STAMP))
            return out
        train = always_redraw(lambda: spikes_upto(r.get_value()))
        def grow(rt):
            self.play(Transform(walls_lbl, grow_l), FadeIn(ax), FadeIn(circ), FadeIn(train), run_time=rt / 8)
            self.play(r.animate.set_value(4.2), run_time=rt * 0.6, rate_func=lambda t: t)
        p.beat(0.7, grow)
        # the stamp grows up
        early = lbl("early reflections", 20, STAMP).next_to(ax, DOWN, buff=0.2).align_to(ax, LEFT)
        late = lbl("late reverb", 20, ECHO).next_to(ax, DOWN, buff=0.2).align_to(ax, RIGHT)
        p.beat(0.88, lambda rt: self.play(FadeIn(early), FadeIn(late), run_time=min(1, rt / 2)))
        land = say("This is the room.", 30, INK)
        p.beat(1.0, lambda rt: self.play(FadeIn(land), run_time=min(1, rt)))


class Scene05Grid(RoomScene):
    """The reveal.  Rows = senders (input time), columns = arrivals (output time)."""
    scene_id = "05"

    def construct(self):
        p = self.pacer
        self.add(head("The grid: rows and columns"))
        n = 7
        h = np.array([1.0, 0.0, 0.6, 0.0, 0.3])
        x = np.array([0.0, 1.0, 0.0, -0.6, 0.0, 0.8, 0.4])
        M = n + len(h) - 1
        G = np.zeros((n, M))
        for k in range(n):
            for j, hv in enumerate(h):
                G[k, k + j] = x[k] * hv
        cs = 0.46
        grid = matrix_grid(np.abs(G), cell=cs).shift(RIGHT * 1.2 + DOWN * 0.1)
        for k in range(n):
            for j in range(M):
                if G[k, j] < 0:
                    cell(grid, k, j).set_fill(CORAL, opacity=min(0.9, abs(G[k, j])))

        # --- Step 1: slice -------------------------------------------------------
        sx = np.linspace(0, 1, 200)
        wave_ax = Axes(x_range=[0, 1, 1], y_range=[-1, 1, 1], x_length=3.6, y_length=1.4,
                       axis_config={"color": INK_DIM, "include_ticks": False}).to_edge(LEFT, buff=0.5).shift(UP * 1.8)
        w = curve_on(wave_ax, sx, np.interp(sx, np.linspace(0, 1, n), x), SIGNAL)
        strips = VGroup(*[Line(wave_ax.c2p(i / (n - 1), 0), wave_ax.c2p(i / (n - 1), x[i]),
                               stroke_width=6, color=SIGNAL) for i in range(n)])
        br = Brace(Line(wave_ax.c2p(1 / (n - 1), -1), wave_ax.c2p(2 / (n - 1), -1)), DOWN, color=INK_DIM, buff=0.05)
        dl = tex(r"\Delta", size=28, color=INK_DIM).next_to(br, DOWN, buff=0.05)
        sl = tex(r"x(k\Delta)\cdot\Delta", size=24, color=SIGNAL).next_to(wave_ax, DOWN, buff=0.55)
        p.beat(0.12, lambda rt: (self.play(FadeIn(wave_ax), Create(w), run_time=rt / 4),
                                 self.play(FadeIn(strips), FadeIn(br), Write(dl), run_time=rt / 4),
                                 self.play(Write(sl), run_time=rt / 4)))

        # --- Step 2: build the grid ---------------------------------------------
        rows_lbl = lbl("input time", 18).next_to(grid, LEFT, buff=0.3).rotate(1.5708)
        cols_lbl = lbl("output time", 18).next_to(grid, DOWN, buff=0.15)
        frame = VGroup(*[cell(grid, k, j).copy().set_fill(opacity=0) for k in range(n) for j in range(M)])
        row_spikes = VGroup(*[Line(cell(grid, k, 0).get_center() + LEFT * 0.7,
                                   cell(grid, k, 0).get_center() + LEFT * (0.7 - 0.5 * abs(x[k])),
                                   stroke_width=5, color=SIGNAL) for k in range(n)])
        def build(rt):
            self.play(FadeIn(frame), FadeIn(rows_lbl), FadeIn(cols_lbl), FadeIn(row_spikes), run_time=rt / 5)
            self.play(*[FadeIn(cell(grid, k, j)) for k in range(n) for j in range(M)
                        if G[k, j] != 0 or True], lag_ratio=0.0, run_time=rt / 3)
        p.beat(0.32, build)

        # --- Step 3: read the rows ----------------------------------------------
        rowbox = Rectangle(width=cs * M, height=cs, stroke_color=SIGNAL, stroke_width=4).move_to(
            VGroup(*[cell(grid, 0, j) for j in range(M)]))
        row_say = lbl("each moment of the guitar launches its own copy of the room", 20, SIGNAL
                      ).to_edge(DOWN, buff=1.05)
        def rows(rt):
            self.play(Create(rowbox), FadeIn(row_say), run_time=rt / 8)
            for k in range(1, n):
                self.play(rowbox.animate.move_to(VGroup(*[cell(grid, k, j) for j in range(M)])),
                          run_time=rt * 0.7 / (n - 1))
        p.beat(0.5, rows)
        self.play(FadeOut(rowbox), run_time=0.2)

        # --- Step 4: read a column: h backwards ---------------------------------
        c = 5
        colbox = Rectangle(width=cs, height=cs * n, stroke_color=STAMP, stroke_width=4).move_to(
            VGroup(*[cell(grid, k, c) for k in range(n)]))
        col_say = lbl("everything in this column arrives now; reading down, the stamp runs backwards",
                      20, STAMP).to_edge(DOWN, buff=1.05)
        ticks = VGroup(*[lbl(f"h[{c - k}]", 14, STAMP).next_to(cell(grid, k, c), RIGHT, buff=0.08)
                         for k in range(n) if 0 <= c - k < len(h)])
        p.beat(0.62, lambda rt: (self.play(Create(colbox), Transform(row_say, col_say), run_time=rt / 4),
                                 self.play(FadeIn(ticks), run_time=rt / 3)))

        # --- Step 5: sum the columns ---------------------------------------------
        y = G.sum(axis=0)
        out_ax = Axes(x_range=[0, M, 1], y_range=[-1, 1.5, 1], x_length=cs * M, y_length=1.2,
                      axis_config={"color": INK_DIM, "include_ticks": False}).next_to(grid, DOWN, buff=0.55)
        out_ax.align_to(grid, LEFT)
        stems = VGroup(*[Line(out_ax.c2p(j + 0.5, 0), out_ax.c2p(j + 0.5, y[j]), stroke_width=6, color=EIGEN)
                         for j in range(M)])
        def sumcols(rt):
            self.play(FadeOut(ticks), FadeIn(out_ax), run_time=rt / 8)
            self.play(colbox.animate.move_to(VGroup(*[cell(grid, k, 0) for k in range(n)])), run_time=0.1)
            for j in range(M):
                self.play(colbox.animate.move_to(VGroup(*[cell(grid, k, j) for k in range(n)])),
                          Create(stems[j]), run_time=rt * 0.6 / M)
        p.beat(0.78, sumcols)
        self.play(FadeOut(colbox), run_time=0.2)

        # --- captions: sum, then the integral ------------------------------------
        riemann = tex(r"y(t)", r"\approx", r"\sum_k", r"x(k\Delta)", r"h(t-k\Delta)", r"\,\Delta",
                      size=34).to_corner(UP + RIGHT, buff=0.7).shift(DOWN * 0.9)
        integral = tex(r"y(t)", r"=", r"\int", r"x(\tau)", r"h(t-\tau)", r"\,d\tau",
                       size=34).move_to(riemann)
        p.beat(0.88, lambda rt: self.play(FadeOut(sl), Write(riemann), run_time=min(1.5, rt / 2)))
        shrink = lbl("Δ shrinks: rows thin into a sheet", 18, INK_DIM).next_to(riemann, DOWN, buff=0.25)
        p.beat(1.0, lambda rt: (self.play(FadeIn(shrink), run_time=rt / 5),
                                self.play(TransformMatchingTex(riemann, integral), run_time=rt / 2)))
