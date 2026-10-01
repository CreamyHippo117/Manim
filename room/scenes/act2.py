"""Act II -- The room's matrix (scenes 4-6)."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Circle, Create, Dot, FadeIn, FadeOut, Line,
    Rectangle, Text, Transform, VGroup, ValueTracker, Write, always_redraw,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from room.config import CORAL, ECHO, GHOST, INK, INK_DIM, ODE, SIGNAL, STAMP  # noqa: E402
from room.core import (  # noqa: E402
    RoomScene, cell, curve_on, head, matrix_grid, ode_note, say, tex,
)
from room import mathcore as mc  # noqa: E402


class Scene04ImageSources(RoomScene):
    scene_id = "04"

    def construct(self):
        p = self.pacer
        self.add(head("A room is one wall, recursively"))
        pts = mc.image_sources(order=3)
        scale = 0.32
        lattice = VGroup()
        for x, y, order in pts:
            d = Dot([x * scale - 3.4, y * scale - 1.6, 0], radius=0.06,
                    color=STAMP if order == 0 else ECHO).set_opacity(max(0.25, 1 - order * 0.13))
            lattice.add(d)
        lattice.set_z_index(1)
        room = Rectangle(width=6 * scale, height=4 * scale, stroke_color=INK_DIM
                         ).move_to([2 * scale - 3.4 + 0.0, 2 * scale - 1.6, 0])
        room.move_to([3 * scale - 3.4, 2 * scale - 1.6, 0])
        rooms = VGroup()
        for i in range(-3, 4):
            for j in range(-3, 4):
                rooms.add(Rectangle(width=6 * scale, height=4 * scale,
                                    stroke_width=0.8, stroke_color=GHOST
                                    ).move_to([(3 + 6 * i) * scale - 3.4,
                                               (2 + 4 * j) * scale - 1.6, 0]))

        def tile(rt):
            self.play(Create(room), run_time=rt / 5)
            self.play(FadeIn(rooms, lag_ratio=0.02), run_time=rt / 3)
            self.play(FadeIn(lattice, lag_ratio=0.02), run_time=rt / 3)
        p.beat(0.3, tile)

        spikes = tex(r"h(t)=\sum_k a_k\,\delta(t-\tau_k)", size=36
                     ).to_edge(RIGHT, buff=0.6).shift(UP * 2.4)
        dens = tex(r"\frac{dN}{dt}\approx\frac{4\pi c^3 t^2}{V}", size=36
                   ).next_to(spikes, DOWN, buff=0.5)
        nums = Text("100 m³: ~1,000 arrivals/s by 15 ms, ~10,000 by 45 ms",
                    font_size=19, color=INK_DIM).next_to(dens, DOWN, buff=0.35)
        p.beat(0.5, lambda rt: self.play(Write(spikes), run_time=rt / 2))
        p.beat(0.7, lambda rt: self.play(Write(dens), FadeIn(nums), run_time=rt / 2))

        # envelope under the spike train
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 1], x_length=4.6, y_length=1.5,
                  axis_config={"color": INK_DIM, "include_ticks": False}
                  ).to_edge(RIGHT, buff=0.7).shift(DOWN * 1.7)
        rng = np.random.default_rng(3)
        ts = np.sort(rng.random(120) ** 0.6)
        stems = VGroup(*[Line(ax.c2p(t, 0), ax.c2p(t, np.exp(-3 * t) * rng.random() * 0.9 + 0.03),
                              stroke_width=2, color=STAMP) for t in ts])
        xs = np.linspace(0, 1, 60)
        env = curve_on(ax, xs, np.exp(-3 * xs), CORAL, 3)
        env_lbl = tex(r"e^{-\sigma t}", size=28, color=CORAL).next_to(env, UP, buff=0.05)
        hook = ode_note(r"\text{envelope of an underdamped oscillator}", size=22
                        ).next_to(ax, DOWN, buff=0.25)
        rt60 = tex(r"\mathrm{RT60}:\ \text{time to fall 60 dB}", size=24
                   ).next_to(hook, DOWN, buff=0.2)

        def envelope(rt):
            self.play(FadeIn(ax), FadeIn(stems, lag_ratio=0.02), run_time=rt / 3)
            self.play(Create(env), Write(env_lbl), run_time=rt / 4)
            self.play(Write(hook), Write(rt60), run_time=rt / 4)
        p.beat(1.0, envelope)


class Scene05Toeplitz(RoomScene):
    """The reveal: constant diagonals."""
    scene_id = "05"

    def construct(self):
        p = self.pacer
        self.add(head("Constant diagonals: the Toeplitz grid"))
        n = 8
        h = np.array([1.0, 0.0, 0.0, 0.6, 0.0, 0.3])
        H = mc.toeplitz_lower(h, n)
        cs = 0.46
        empty = matrix_grid(np.zeros((n, n)), cell=cs).shift(LEFT * 3.3 + DOWN * 0.4)
        full = matrix_grid(H, cell=cs).move_to(empty)
        self.add(empty)

        # fill column by column: each column is the stamp, shifted one step down
        cols = [VGroup(*[cell(full, i, k) for i in range(n) if H[i, k] > 0])
                for k in range(n)]
        note = say("column k: the stamp, shifted to start at k", color=INK_DIM)

        def fill(rt):
            self.play(FadeIn(note), run_time=rt / 8)
            for k in range(n):
                self.play(FadeIn(cols[k]), run_time=rt / (n + 2))
        p.beat(0.3, fill)

        # light the main diagonal, then the echo diagonal
        main = VGroup(*[cell(full, i, i) for i in range(n)])
        echo = VGroup(*[cell(full, i + 3, i) for i in range(n - 3)])
        hl1 = Text("h[0]: direct sound", font_size=20, color=STAMP
                   ).next_to(empty, RIGHT, buff=0.5).shift(UP * 1.6)
        hl2 = Text("h[3]: the wall echo", font_size=20, color=ECHO
                   ).next_to(hl1, DOWN, buff=0.3, aligned_edge=LEFT)

        def read(rt):
            self.play(main.animate.set_stroke(STAMP, 3), FadeIn(hl1), run_time=rt / 3)
            self.play(echo.animate.set_stroke(ECHO, 3), FadeIn(hl2), run_time=rt / 3)
        p.beat(0.5, read)

        entries = tex(r"H_{nk}=h[n-k],\qquad y[n]=\sum_k h[n-k]\,x[k]", size=34
                      ).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.1)
        p.beat(0.6, lambda rt: self.play(Write(entries), run_time=rt / 2))

        # columns vs rows: a row shows h reversed
        row = Rectangle(width=cs * n, height=cs, stroke_color=SIGNAL, stroke_width=4
                        ).move_to(cell(full, 5, 3).get_center()).align_to(full, LEFT)
        row_note = Text("row n: everything arriving at output time n (h reads backward)",
                        font_size=19, color=SIGNAL).next_to(entries, DOWN, buff=0.35)
        p.beat(0.75, lambda rt: self.play(Create(row), FadeIn(row_note), run_time=rt / 2))

        # continuous limit
        lim = tex(r"y(t)\approx\sum_k x(k\Delta)\,h(t-k\Delta)\,\Delta"
                  r"\;\longrightarrow\;\int x(\tau)\,h(t-\tau)\,d\tau", size=28
                  ).to_edge(DOWN, buff=1.0)
        shrink = Text("shrink the sample spacing Δ: grid becomes a sheet, row sum becomes an integral",
                      font_size=18, color=INK_DIM).next_to(lim, UP, buff=0.2)
        p.beat(1.0, lambda rt: (self.play(FadeIn(shrink), run_time=rt / 4),
                                self.play(Write(lim), run_time=rt / 2)))


class Scene06Duhamel(RoomScene):
    scene_id = "06"

    def construct(self):
        p = self.pacer
        self.add(head("Duhamel: you've seen this matrix"))
        n = 8
        k = 0.45
        g = np.exp(-k * np.arange(n))
        H = mc.toeplitz_lower(g, n)
        grid = matrix_grid(H, cell=0.46).shift(LEFT * 3.6 + DOWN * 0.5)
        ode = tex(r"y'+ky=f,\quad y(0)=0", size=34).next_to(grid, UP, buff=0.5)
        stamp = tex(r"g(t)=e^{-kt},\ t\ge 0", size=28, color=STAMP).next_to(grid, DOWN, buff=0.4)

        def build(rt):
            self.play(Write(ode), run_time=rt / 4)
            self.play(FadeIn(grid, lag_ratio=0.01), Write(stamp), run_time=rt / 2)
        p.beat(0.4, build)

        duh = tex(r"y(t)=\int_0^t e^{-k(t-\tau)}\,f(\tau)\,d\tau=(g*f)(t)", size=32
                  ).to_edge(RIGHT, buff=0.5).shift(UP * 1.4)
        room = tex(r"y(t)=\int h(t-\tau)\,x(\tau)\,d\tau", size=32, color=SIGNAL
                   ).next_to(duh, DOWN, buff=0.5)
        side = Text("side by side with the room's integral", font_size=18,
                    color=INK_DIM).next_to(room, DOWN, buff=0.3)
        p.beat(0.65, lambda rt: (self.play(Write(duh), run_time=rt / 3),
                                 self.play(Write(room), FadeIn(side), run_time=rt / 3)))

        # point at the triangle: zero above the diagonal = causality
        upper = VGroup(*[grid[i * n + j] for i in range(n) for j in range(n) if j > i])
        tri = Text("zero above the diagonal: nothing arrives before it's sent",
                   font_size=20, color=ECHO).to_edge(RIGHT, buff=0.5).shift(DOWN * 1.6)
        tri.scale(0.98)
        callbk = ode_note(r"\text{the integrating-factor formula was always a convolution}",
                          size=22).next_to(tri, DOWN, buff=0.35)
        p.beat(1.0, lambda rt: (self.play(upper.animate.set_stroke(ECHO, 2, opacity=0.9),
                                          FadeIn(tri), run_time=rt / 3),
                                self.play(Write(callbk), run_time=rt / 4)))
