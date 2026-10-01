"""Act IV -- Bottle a room (scene 11)."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Create, FadeIn, FadeOut, Line, Rectangle, Text,
    Transform, VGroup, ValueTracker, Write, always_redraw,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from room.config import CORAL, ECHO, EIGEN, GHOST, INK, INK_DIM, ODE, SIGNAL, STAMP  # noqa: E402
from room.core import (  # noqa: E402
    RoomScene, cell, curve_on, head, matrix_grid, ode_note, say, tex,
)
from room import mathcore as mc  # noqa: E402


class Scene11InvertPadRace(RoomScene):
    scene_id = "11"

    def construct(self):
        p = self.pacer
        self.add(head("Invert, pad, and race"))

        # --- measuring = inverting the diagonal ---------------------------------
        ax = Axes(x_range=[0, 10, 5], y_range=[0, 6, 3], x_length=5.4, y_length=2.4,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(LEFT * 3.4 + UP * 1.4)
        rng = np.random.default_rng(1)
        w = np.linspace(0.2, 10, 120)
        X = np.abs(np.sinc(w / 10) * 2 + 0.05 * rng.standard_normal(w.size)) + 0.01
        X[60:64] = 0.004            # tiny eigenvalues
        quotient = np.minimum(1.0 / X, 6)
        fixed = X / (X**2 + 0.05)
        raw = curve_on(ax, w, quotient, CORAL)
        floor = curve_on(ax, w, np.minimum(fixed, 6), EIGEN)
        eq_h = tex(r"\hat H(\omega)=\frac{Y(\omega)\,\overline{X(\omega)}}{|X(\omega)|^2+\varepsilon}",
                   size=30).next_to(ax, DOWN, buff=0.5)
        cap = Text("where X is tiny, Y/X explodes: ill-conditioned", font_size=18,
                   color=CORAL).next_to(ax, UP, buff=0.15)

        def measure(rt):
            self.play(FadeIn(ax), Create(raw), FadeIn(cap), run_time=rt / 4)
            self.play(Transform(raw, floor), Write(eq_h), run_time=rt / 4)
        p.beat(0.2, measure)
        spoken = say("a sine sweep keeps X strong at every frequency, so nothing needs a floor", size=18)
        p.beat(0.28, lambda rt: self.play(FadeIn(spoken), run_time=min(rt, 1)))

        # --- the circulant caveat: wrap, then pad -------------------------------
        n = 8
        h = np.array([1, 0, 0, 0.6, 0, 0.3, 0, 0.0])
        circ = mc.circulant(np.array([1, 0, 0, 0.6, 0, 0.3]), n)
        toep = mc.toeplitz_lower(np.array([1, 0, 0, 0.6, 0, 0.3]), n)
        g1 = matrix_grid(toep, cell=0.34).shift(RIGHT * 3.0 + UP * 1.4)
        g2 = matrix_grid(circ, cell=0.34).move_to(g1)
        wrap = Text("diagonals wrap round the corner: echoes smear onto the start",
                    font_size=17, color=ECHO).next_to(g1, DOWN, buff=0.25)
        pad = tex(r"\text{pad to } N+M-1:\ \text{wrapped part lands on zeros}", size=24, color=EIGEN
                  ).next_to(wrap, DOWN, buff=0.2)
        fft_c = Text("padded circulant = Toeplitz   (fftconvolve does exactly this)", font_size=18,
                     color=INK_DIM).next_to(pad, DOWN, buff=0.2)

        def caveat(rt):
            self.play(FadeIn(g1), run_time=rt / 6)
            self.play(Transform(g1, g2), FadeIn(wrap), run_time=rt / 4)
            self.play(Write(pad), FadeIn(fft_c), run_time=rt / 4)
        p.beat(0.5, caveat)

        # --- race ---------------------------------------------------------------
        N, M = 480_000, 96_000
        d_ops, f_ops = mc.direct_ops(N, M), mc.fft_ops(N, M)
        self.play(FadeOut(VGroup(ax, raw, cap, eq_h, g1, wrap, pad, fft_c, spoken)), run_time=0.4)
        left_box = Rectangle(width=5.4, height=0.6, stroke_color=CORAL).shift(LEFT * 3.2 + DOWN * 0.4)
        right_box = Rectangle(width=5.4, height=0.6, stroke_color=EIGEN).shift(RIGHT * 3.2 + DOWN * 0.4)
        t = ValueTracker(0.0)
        lbar = always_redraw(lambda: Rectangle(width=max(1e-3, 5.4 * min(1, t.get_value())), height=0.6,
                                               stroke_width=0, fill_color=CORAL, fill_opacity=0.8
                                               ).align_to(left_box, LEFT).align_to(left_box, UP))
        # real ratio ~ 1000x: the right bar finishes in 1/1000 of the time
        rbar = always_redraw(lambda: Rectangle(width=max(1e-3, 5.4 * min(1, t.get_value() * 400)), height=0.6,
                                               stroke_width=0, fill_color=EIGEN, fill_opacity=0.8
                                               ).align_to(right_box, LEFT).align_to(right_box, UP))
        l_t = tex(rf"\mathbf{{H}}\mathbf{{x}}:\ NM\approx {d_ops/1e10:.1f}\times10^{{10}}", size=28,
                  color=CORAL).next_to(left_box, UP, buff=0.3)
        r_t = tex(rf"\mathbf{{F}}\to\boldsymbol\Lambda\to\mathbf{{F}}^{{-1}}:\ \sim{f_ops/1e6:.0f}\times10^{{6}}\ \text{{(times a small constant)}}",
                  size=24, color=EIGEN).next_to(right_box, UP, buff=0.3)
        same = Text("same answer, about a thousand times fewer steps: that is the diagonalization",
                    font_size=19, color=INK_DIM).shift(DOWN * 1.5)

        def race(rt):
            self.play(Create(left_box), Create(right_box), Write(l_t), Write(r_t), run_time=rt / 5)
            self.add(lbar, rbar)
            self.play(t.animate.set_value(1.0), run_time=rt / 2, rate_func=lambda x: x)
            self.play(FadeIn(same), run_time=rt / 6)
        p.beat(0.7, race)

        # --- A/B + close --------------------------------------------------------
        self.play(FadeOut(VGroup(left_box, right_box, lbar, rbar, l_t, r_t, same)), run_time=0.4)
        names = ["dry", "stairwell", "bathroom", "closet", "parking garage"]
        rows = VGroup()
        for i, nm in enumerate(names):
            hh = np.zeros(10)
            hh[0] = 1
            if i:
                hh[2 + i] = 0.8 / i
            ab = VGroup(Text(nm, font_size=18, color=INK).set_width(1.5),
                        matrix_grid(mc.toeplitz_lower(hh, 6), cell=0.2),
                        )
            ab.arrange(RIGHT, buff=0.3)
            rows.add(ab)
        rows.arrange(DOWN, buff=0.25, aligned_edge=LEFT).shift(UP * 0.2)
        stamp_note = Text("each room: its stamp, its Toeplitz band, its EQ diagonal",
                          font_size=18, color=INK_DIM).next_to(rows, DOWN, buff=0.4)
        p.beat(0.82, lambda rt: self.play(FadeIn(rows, lag_ratio=0.2), FadeIn(stamp_note), run_time=rt / 2))

        self.play(FadeOut(VGroup(rows, stamp_note)), run_time=0.4)
        table = VGroup(
            tex(r"\text{a room makes copies}\ \Rightarrow\ \text{Toeplitz matrix}", size=30),
            tex(r"\text{copies of a sine are a sine}\ \Rightarrow\ \text{eigenvectors}", size=30),
            tex(r"\text{so a room is an EQ}\ \Rightarrow\ \mathbf{H}=\mathbf{F}^{-1}\boldsymbol\Lambda\mathbf{F}", size=30),
        ).arrange(DOWN, buff=0.5).shift(UP * 0.3)
        end = Text("A room is a matrix. Diagonalize it and it's an EQ.", font_size=28,
                   color=STAMP).next_to(table, DOWN, buff=0.7)
        p.beat(0.94, lambda rt: (self.play(FadeIn(table, lag_ratio=0.5), run_time=rt / 2),
                                 self.play(Write(end), run_time=rt / 3)))
        bridge = Text("How does sound cancel itself? Next time.", font_size=24, color=INK_DIM
                      ).to_edge(DOWN, buff=1.1)
        p.beat(1.0, lambda rt: self.play(FadeIn(bridge), run_time=min(rt, 1)))
