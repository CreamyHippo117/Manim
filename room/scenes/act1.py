"""Act I -- A room makes copies (scenes 0-3)."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Circle, Create, DashedLine, Dot, FadeIn,
    FadeOut, Line, Polygon, Rectangle, Transform, VGroup, Write, ValueTracker,
    always_redraw, Arrow, Text,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from room.config import CORAL, ECHO, GHOST, GOLD, INK, INK_DIM, ODE, SIGNAL, STAMP, TEAL  # noqa: E402
from room.core import (  # noqa: E402
    RoomScene, column_vector, curve_on, head, matrix_grid, ode_note, say,
    stem_plot, tex,
)
from room import mathcore as mc  # noqa: E402


class Scene00ColdOpen(RoomScene):
    """Dry guitar, then the stairwell.  No math on screen."""
    scene_id = "00"

    def construct(self):
        p = self.pacer
        ax = Axes(x_range=[0, 4, 1], y_range=[-1, 1, 1], x_length=10, y_length=2.4,
                  axis_config={"color": INK_DIM, "stroke_width": 1.5,
                               "include_ticks": False})
        t = np.linspace(0, 4, 700)
        dry = np.exp(-t * 6) * np.sin(2 * np.pi * 9 * t) * 0.9
        # the same pluck, smeared by an exponential tail: "the stairwell"
        wet = np.convolve(dry, np.exp(-np.arange(300) / 60) * 0.12)[:len(t)]
        label1 = Text("a dry guitar", font_size=28, color=INK_DIM).next_to(ax, UP)
        wave1 = curve_on(ax, t, dry, SIGNAL)

        def first(rt):
            self.play(FadeIn(ax), FadeIn(label1), run_time=min(1.0, rt / 4))
            self.play(Create(wave1), run_time=rt / 2)
        p.beat(0.4, first)

        label2 = Text("the same guitar, in a stairwell", font_size=28,
                      color=STAMP).next_to(ax, UP)
        wave2 = curve_on(ax, t, wet, STAMP)

        def second(rt):
            self.play(Transform(label1, label2), Transform(wave1, wave2),
                      run_time=rt / 2)
        p.beat(0.8, second)
        line = say("By the end, this room will be a matrix you can diagonalize.",
                   size=26, color=INK)
        p.beat(1.0, lambda rt: self.play(FadeIn(line), run_time=min(1, rt)))


class Scene01Impulse(RoomScene):
    scene_id = "01"

    def construct(self):
        p = self.pacer
        title = head("An impulse is anything shorter than the room can resolve")
        self.add(title)

        ax = Axes(x_range=[-1, 1, 1], y_range=[0, 5.2, 1], x_length=5, y_length=2.8,
                  axis_config={"color": INK_DIM, "include_ticks": False}
                  ).shift(LEFT * 3.2 + DOWN * 0.3)
        eps = ValueTracker(1.0)

        def pulse():
            e = eps.get_value()
            r = Polygon(ax.c2p(-e / 2, 0), ax.c2p(-e / 2, 1 / e), ax.c2p(e / 2, 1 / e),
                        ax.c2p(e / 2, 0), stroke_color=SIGNAL, stroke_width=3,
                        fill_color=SIGNAL, fill_opacity=0.35)
            return r
        shape = always_redraw(pulse)
        area = say("area stays 1 as the width shrinks", color=INK_DIM)

        def squeeze(rt):
            self.play(FadeIn(ax), FadeIn(shape), FadeIn(area), run_time=min(1.2, rt / 4))
            self.play(eps.animate.set_value(0.2), run_time=rt / 2)
        p.beat(0.25, squeeze)

        # sifting: the strip collapses onto f(t0) under a smooth curve
        ax2 = Axes(x_range=[-1, 1, 1], y_range=[0, 2, 1], x_length=5, y_length=2.8,
                   axis_config={"color": INK_DIM, "include_ticks": False}
                   ).shift(RIGHT * 3.2 + DOWN * 0.3)
        xs = np.linspace(-1, 1, 100)
        f = curve_on(ax2, xs, 1 + 0.5 * np.sin(2.2 * xs), INK)
        t0 = 0.3
        e2 = ValueTracker(0.5)

        def strip():
            e = e2.get_value()
            yv = 1 + 0.5 * np.sin(2.2 * t0)
            return Rectangle(width=ax2.c2p(e, 0)[0] - ax2.c2p(0, 0)[0],
                             height=ax2.c2p(0, yv)[1] - ax2.c2p(0, 0)[1],
                             stroke_width=0, fill_color=STAMP, fill_opacity=0.45
                             ).move_to(ax2.c2p(t0, yv / 2))
        strip_m = always_redraw(strip)
        sift = tex(r"\int f(t)\,\delta(t-t_0)\,dt = f(t_0)", size=34
                   ).next_to(ax2, UP, buff=0.5)

        def under(rt):
            self.play(FadeIn(ax2), Create(f), FadeIn(strip_m), run_time=rt / 4)
            self.play(e2.animate.set_value(0.02), run_time=rt / 2)
            self.play(Write(sift), run_time=rt / 4)
        p.beat(0.55, under)

        # discrete version: a single lit entry in a column of zeros
        col = column_vector(8, lit=0).move_to(LEFT * 5.7 + UP * 1.5).scale(0.7)
        dlt = tex(r"\delta[n]", size=30, color=STAMP).next_to(col, DOWN, buff=0.2)

        def discrete(rt):
            self.play(FadeIn(col), Write(dlt), run_time=rt / 2)
        p.beat(0.8, discrete)

        hook = ode_note(r"\mathcal{L}\{\delta(t-t_0)\}=e^{-st_0}", size=30
                        ).to_edge(RIGHT, buff=0.6).shift(UP * 2.5)
        p.beat(1.0, lambda rt: self.play(Write(hook), run_time=min(rt, 1.5)))


class Scene02Mirrors(RoomScene):
    scene_id = "02"

    def construct(self):
        p = self.pacer
        self.add(head("Walls are mirrors"))
        wall_x = 1.0
        wall = Line([wall_x, -2.2, 0], [wall_x, 2.2, 0], stroke_width=8, color=INK_DIM)
        src = Dot([-2.5, 0.4, 0], color=SIGNAL, radius=0.1)
        mic = Dot([-2.5, -1.0, 0], color=INK, radius=0.1)
        img = Dot([2 * wall_x + 2.5, 0.4, 0], color=SIGNAL, radius=0.1,
                  fill_opacity=0.35)
        hit = [wall_x, -0.15, 0]
        bent = VGroup(Line(src.get_center(), hit, color=ECHO),
                      Line(hit, mic.get_center(), color=ECHO))
        straight = DashedLine(img.get_center(), mic.get_center(), color=ECHO)
        direct = Line(src.get_center(), mic.get_center(), color=SIGNAL)

        def setup(rt):
            self.play(Create(wall), FadeIn(src), FadeIn(mic), run_time=rt / 4)
            self.play(Create(direct), Create(bent), run_time=rt / 4)
            self.play(FadeIn(img), Create(straight), run_time=rt / 3)
        p.beat(0.3, setup)

        num = tex(r"\frac{3.4\ \text{m}}{340\ \text{m/s}} = 10\ \text{ms}", size=34
                  ).to_edge(RIGHT, buff=0.7).shift(UP * 1.8)
        sym = tex(r"\tau = \frac{\Delta d}{c}, \qquad a = \frac{r_1}{r_2}\,R", size=34
                  ).next_to(num, DOWN, buff=0.5)
        p.beat(0.55, lambda rt: self.play(Write(num), run_time=rt / 2))
        p.beat(0.7, lambda rt: self.play(Write(sym), run_time=rt / 2))

        # the stamp, lifted off the time axis in its permanent colour
        axh = Axes(x_range=[0, 3, 1], y_range=[0, 1.2, 1], x_length=4.2, y_length=1.5,
                   axis_config={"color": INK_DIM, "include_ticks": False}
                   ).to_edge(RIGHT, buff=0.7).shift(DOWN * 1.1)
        s0 = Line(axh.c2p(0, 0), axh.c2p(0, 1), color=STAMP, stroke_width=7)
        s1 = Line(axh.c2p(1.6, 0), axh.c2p(1.6, 0.6), color=STAMP, stroke_width=7)
        stamp = tex(r"h(t)=\delta(t)+a\,\delta(t-\tau)", size=32, color=STAMP
                    ).next_to(axh, DOWN, buff=0.3)
        ledger = tex(r"H(s)=1+a\,e^{-s\tau}", size=30, color=STAMP)
        ledger.to_corner(RIGHT + DOWN, buff=0.5).shift(UP * 0.5)
        shift = ode_note(r"\text{shift theorem}", size=22).next_to(ledger, LEFT, buff=0.4)

        def lift(rt):
            self.play(FadeIn(axh), Create(s0), Create(s1), run_time=rt / 3)
            self.play(Write(stamp), run_time=rt / 3)
        p.beat(0.88, lift)
        p.beat(1.0, lambda rt: self.play(Write(ledger), FadeIn(shift), run_time=rt / 2))


class Scene03Linear(RoomScene):
    scene_id = "03"

    def construct(self):
        p = self.pacer
        self.add(head("Linear means \"is a matrix\""))
        # clipper vs room, two claps
        ax = Axes(x_range=[0, 6, 1], y_range=[-1.5, 1.5, 1], x_length=6, y_length=2.2,
                  axis_config={"color": INK_DIM, "include_ticks": False}
                  ).shift(LEFT * 3.4 + UP * 1.2)
        xs = np.linspace(0, 6, 300)
        c1 = np.exp(-((xs - 1.5) / 0.15) ** 2)
        c2 = np.exp(-((xs - 3.0) / 0.15) ** 2) * 0.9
        both = c1 + c2
        clip = np.clip(both * 1.6, -1, 1) / 1.6
        summed = c1 + c2
        sep = curve_on(ax, xs, c1 + c2, GHOST, 2)
        out_room = curve_on(ax, xs, summed, SIGNAL)
        out_clip = curve_on(ax, xs, np.clip(1.6 * c1, 0, 1) / 1.6 + np.clip(1.6 * c2, 0, 1) / 1.6 * 0 + 0.0 * xs, CORAL)
        clip_total = curve_on(ax, xs, np.clip(1.6 * both, -1, 1) / 1.6, CORAL)
        verdict = Text("clipper: misses the dashed sum   |   room: lands on it",
                       font_size=22, color=INK_DIM).next_to(ax, DOWN)

        def claps(rt):
            self.play(FadeIn(ax), Create(sep), run_time=rt / 4)
            self.play(Create(clip_total), run_time=rt / 4)
            self.play(Create(out_room), FadeIn(verdict), run_time=rt / 4)
        p.beat(0.35, claps)

        # the matrix: columns are "what the room does to a clap at time k"
        n = 6
        H = mc.toeplitz_lower(np.array([1.0, 0.0, 0.5, 0.25]), n)
        grid = matrix_grid(H, cell=0.5).shift(RIGHT * 3.2 + DOWN * 0.8)
        x_col = column_vector(n, 0.5).next_to(grid, RIGHT, buff=0.6)
        eqn = tex(r"\mathbf{y}=\mathbf{H}\,\mathbf{x}", size=44).next_to(grid, UP, buff=0.5)
        col_hl = Rectangle(width=0.5, height=0.5 * n, stroke_color=GOLD, stroke_width=4
                           ).move_to(grid[0].get_center() + DOWN * 0.5 * (n - 1) / 2)
        point = Text("column k = the room's reply to a clap at time k",
                     font_size=20, color=GOLD).next_to(grid, DOWN, buff=0.35)

        def matrix(rt):
            self.play(FadeIn(grid), FadeIn(x_col), Write(eqn), run_time=rt / 3)
            self.play(Create(col_hl), FadeIn(point), run_time=rt / 4)
            for k in range(1, 4):
                self.play(col_hl.animate.shift(RIGHT * 0.5), run_time=rt / 14)
        p.beat(0.75, matrix)

        fail = Text("no matrix reproduces the clipper", font_size=24, color=CORAL
                    ).to_edge(LEFT, buff=0.7).shift(DOWN * 1.2)
        hook = ode_note(r"\text{solutions of a linear ODE form a vector space}",
                        size=26).next_to(fail, DOWN, buff=0.4, aligned_edge=LEFT)
        held = say("time invariance: held for the next scene", size=20)

        def close(rt):
            self.play(FadeIn(fail), run_time=rt / 4)
            self.play(Write(hook), FadeIn(held), run_time=rt / 3)
        p.beat(1.0, close)
