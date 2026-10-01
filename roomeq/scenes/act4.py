"""Act IV -- Bottle a room (scene 10)."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Create, FadeIn, FadeOut, Line, Rectangle, Text,
    Transform, VGroup, ValueTracker, Write, always_redraw,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from roomeq.config import CORAL, ECHO, EIGEN, GHOST, GOLD, INK, INK_DIM, SIGNAL, STAMP  # noqa: E402
from roomeq.core import RoomScene, curve_on, head, matrix_grid, say, sliders, tex  # noqa: E402
from roomeq import mathcore as mc  # noqa: E402


def lbl(text, size=20, color=INK_DIM):
    return Text(text, font_size=size, color=color)


class Scene10Bottle(RoomScene):
    scene_id = "10"

    def construct(self):
        p = self.pacer
        self.add(head("Stamping vs EQ, and the A/B"))

        # --- measure ------------------------------------------------------------
        ax = Axes(x_range=[0, 1, 1], y_range=[0, 1, 1], x_length=6, y_length=2.2,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(UP * 0.8)
        rng = np.random.default_rng(4)
        ts = np.sort(rng.random(90) ** 0.7)
        stamp = VGroup(*[Line(ax.c2p(t, 0), ax.c2p(t, np.exp(-3 * t) * (0.4 + 0.5 * rng.random()) + 0.03),
                              stroke_width=3, color=STAMP) for t in ts])
        m = lbl("a mic in a stairwell, a clap: the recorded stamp (a sine sweep does this better)", 20
                ).to_edge(DOWN, buff=1.0)
        p.beat(0.15, lambda rt: self.play(FadeIn(ax), FadeIn(stamp, lag_ratio=0.02), FadeIn(m), run_time=rt / 2))
        self.play(FadeOut(VGroup(ax, stamp, m)), run_time=0.3)

        # --- race ---------------------------------------------------------------
        rate, sx, sh = 48000, 10, 2
        total = mc.direct_conv_ops(sx, sh, rate)
        n, M = 6, 9
        grid = matrix_grid(np.zeros((n, M)) + 0.0, cell=0.3).shift(LEFT * 3.4 + UP * 0.4)
        left_c = tex(r"0", size=40, color=CORAL).next_to(grid, DOWN, buff=0.4)
        lt = lbl("stamping: the grid fills row by row", 20, CORAL).next_to(grid, UP, buff=0.3)
        eqs, _ = sliders([0.9, 0.5, 0.75, 0.3, 0.6, 0.8, 0.4], width=3.8, height=1.5)
        eqs.move_to([3.4, 0.4, 0])
        right_c = tex(r"\text{a tiny fraction}", size=30, color=EIGEN).next_to(eqs, DOWN, buff=0.7)
        rt_l = lbl("EQ: split, turn sliders, recombine", 20, EIGEN).next_to(eqs, UP, buff=0.5)
        code = Text("y = fftconvolve(guitar, room)", font_size=24, color=INK, font="Menlo"
                    ).to_edge(DOWN, buff=1.0)
        cnt = ValueTracker(0.0)
        counter = always_redraw(lambda: tex(rf"{cnt.get_value() / 1e9:.1f}\times10^{{9}}", size=40, color=CORAL
                                            ).next_to(grid, DOWN, buff=0.4))
        fill = VGroup(*[Rectangle(width=0.3 * M, height=0.3, stroke_width=0, fill_color=CORAL, fill_opacity=0.5
                                  ).move_to(grid.get_top() + DOWN * (0.15 + 0.3 * k)) for k in range(n)])
        def race(rt):
            self.play(FadeIn(grid), FadeIn(lt), FadeIn(eqs), FadeIn(rt_l), run_time=rt / 8)
            self.play(FadeIn(right_c), FadeIn(counter), FadeIn(code), run_time=rt / 8)
            self.play(cnt.animate.set_value(total), *[FadeIn(f) for f in fill], run_time=rt / 2,
                      rate_func=lambda t: t)
        p.beat(0.45, race)
        self.play(FadeOut(VGroup(grid, lt, eqs, rt_l, right_c, counter, code, fill)), run_time=0.3)

        # --- A/B ----------------------------------------------------------------
        names = ["dry", "stairwell", "bathroom", "closet", "parking garage"]
        taus = [None, 0.05, 0.02, 0.008, 0.12]
        why = ["", "long tail: big", "sharp low slider: boomy", "dense early spikes: boxy", "very long tail: huge"]
        rows = VGroup()
        for nm, tau, w in zip(names, taus, why):
            axr = Axes(x_range=[0, 1, 1], y_range=[0, 1, 1], x_length=3, y_length=0.55,
                       axis_config={"color": INK_DIM, "include_ticks": False, "stroke_width": 1})
            ts = np.linspace(0, 1, 30)
            spikes = VGroup(Line(axr.c2p(0, 0), axr.c2p(0, 1), color=STAMP, stroke_width=3))
            if tau:
                for t in ts[1:]:
                    spikes.add(Line(axr.c2p(t, 0), axr.c2p(t, 0.5 * np.exp(-t * (0.05 / tau) * 3)),
                                    color=STAMP, stroke_width=2))
            eqr, _ = sliders(list(0.5 + 0.4 * np.cos(np.arange(10) * (1 + (0 if not tau else 0.05 / tau))) * (0 if not tau else 1) + (0.45 if not tau else 0)),
                             width=3, height=0.55)
            row = VGroup(lbl(nm, 20, INK).set_width(1.6), VGroup(axr, spikes), eqr, lbl(w, 16, INK_DIM))
            row.arrange(RIGHT, buff=0.5)
            rows.add(row)
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT).shift(UP * 0.1)
        head_l = lbl("each clip: its stamp and its EQ side by side", 18).next_to(rows, UP, buff=0.3)
        p.beat(0.7, lambda rt: self.play(FadeIn(rows, lag_ratio=0.2), FadeIn(head_l), run_time=rt / 2))
        self.play(FadeOut(VGroup(rows, head_l)), run_time=0.3)

        # --- close: the three sentences ------------------------------------------
        s = VGroup(lbl("A room makes copies.", 32, STAMP),
                   lbl("Copies of a sine wave are still a sine wave.", 32, SIGNAL),
                   lbl("So a room is just an EQ.", 32, EIGEN)).arrange(DOWN, buff=0.7).shift(UP * 0.4)
        p.beat(0.9, lambda rt: self.play(FadeIn(s, lag_ratio=0.6), run_time=rt / 2))
        end = lbl("A room is an EQ. You can bottle it.", 30, INK).to_edge(DOWN, buff=1.5)
        bridge = lbl("How does sound cancel itself? Next time.", 24, INK_DIM).to_edge(DOWN, buff=1.0)
        p.beat(1.0, lambda rt: (self.play(FadeIn(end), run_time=rt / 4), self.play(FadeIn(bridge), run_time=rt / 4)))
