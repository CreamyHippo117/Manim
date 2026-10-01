"""Act III -- A room is an EQ (scenes 6-9).  Math on screen: only Y = H X, scene 7."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, Dot, FadeIn, FadeOut, Line,
    Text, Transform, VGroup, ValueTracker, Write, always_redraw,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from roomeq.config import CORAL, ECHO, EIGEN, GHOST, GOLD, INK, INK_DIM, SIGNAL, STAMP  # noqa: E402
from roomeq.core import RoomScene, curve_on, head, say, sliders, tex  # noqa: E402
from roomeq import mathcore as mc  # noqa: E402


def lbl(text, size=20, color=INK_DIM):
    return Text(text, font_size=size, color=color)


def arrow_chain(origin, vecs, colors, scale):
    """Arrows laid tip to tail from ``origin``."""
    out, cur = VGroup(), np.array(origin, dtype=float)
    for v, col in zip(vecs, colors):
        end = cur + scale * np.array([v.real, v.imag, 0])
        out.add(Arrow(cur, end, buff=0, color=col, stroke_width=5, max_tip_length_to_length_ratio=0.25))
        cur = end
    return out


class Scene06Pure(RoomScene):
    scene_id = "06"

    def construct(self):
        p = self.pacer
        self.add(head("The one sound a room can't change"))
        ask = lbl("what happens to a pure tone?", 24, INK).to_edge(DOWN, buff=1.0)
        t = np.linspace(0, 2, 400)
        axL = Axes(x_range=[0, 2, 1], y_range=[-2, 2, 1], x_length=5.2, y_length=2.0,
                   axis_config={"color": INK_DIM, "include_ticks": False}).shift(LEFT * 3.4 + UP * 1.4)
        axR = axL.copy().shift(RIGHT * 6.8)
        sine = lambda d, a: a * np.sin(2 * np.pi * 3 * (t - d))  # noqa: E731
        guitar = lambda d, a: a * np.exp(-3 * np.clip(t - d, 0, None)) * np.sign(
            np.sin(2 * np.pi * 3 * (t - d)) + 0.4 * np.sin(2 * np.pi * 7 * (t - d))) * (t >= d)  # noqa: E731
        sL = [curve_on(axL, t, sine(0, 1), SIGNAL), curve_on(axL, t, sine(0.07, 0.6), ECHO)]
        sR = [curve_on(axR, t, guitar(0, 1), SIGNAL), curve_on(axR, t, guitar(0.07, 0.6), ECHO)]
        sumL = curve_on(axL, t, sine(0, 1) + sine(0.07, 0.6), STAMP)
        sumR = curve_on(axR, t, guitar(0, 1) + guitar(0.07, 0.6), STAMP)
        capL = lbl("sine + shifted sine = a sine", 20, STAMP).next_to(axL, DOWN)
        capR = lbl("guitar + shifted guitar = a new shape", 20, CORAL).next_to(axR, DOWN)
        p.beat(0.2, lambda rt: self.play(FadeIn(ask), run_time=min(1, rt / 3)))
        def side(rt):
            self.play(FadeIn(axL), FadeIn(axR), *[Create(c) for c in sL + sR], run_time=rt / 3)
            self.play(Create(sumL), Create(sumR), FadeIn(capL), FadeIn(capR), run_time=rt / 3)
        p.beat(0.5, side)
        self.play(FadeOut(VGroup(axL, axR, *sL, *sR, sumL, sumR, capL, capR, ask)), run_time=0.3)
        # phasors: the whole room's echoes laid tip to tail
        delays = [0.0, 0.010, 0.017, 0.031]
        amps = [1.0, 0.6, 0.4, 0.25]
        f = 45.0
        arrows, total = mc.phasor_sum(delays, amps, f)
        origin = [-2.5, -0.8, 0]
        chain = arrow_chain(origin, arrows, [SIGNAL, ECHO, ECHO, ECHO], 2.0)
        res = Arrow(origin, np.array(origin) + 2.0 * np.array([total.real, total.imag, 0]),
                    buff=0, color=STAMP, stroke_width=8)
        spin = lbl("a sine is a spinning arrow's shadow; shifting rotates it, scaling shrinks it", 20
                   ).to_edge(DOWN, buff=1.0)
        res_l = lbl("one arrow: the room's effect on this frequency", 22, STAMP).to_edge(RIGHT, buff=0.7)
        p.beat(0.8, lambda rt: (self.play(FadeIn(spin), Create(chain, lag_ratio=0.7), run_time=rt / 2)))
        p.beat(1.0, lambda rt: self.play(Create(res), FadeIn(res_l), run_time=min(1.5, rt / 2)))


class Scene07EQ(RoomScene):
    scene_id = "07"

    def construct(self):
        p = self.pacer
        self.add(head("A room is an EQ"))
        n = 14
        fs = np.linspace(20, 600, n)
        d = [0.0, 0.010, 0.017, 0.031]
        a = [1.0, 0.6, 0.4, 0.25]
        H = np.array([mc.phasor_sum(d, a, f)[1] for f in fs])
        eq, dots = sliders(np.abs(H) / np.abs(H).max(), width=9, height=2.2, knobs=True)
        eq.shift(DOWN * 0.2 + LEFT * 0.0)
        # centre the group
        eq.move_to([0, -0.3, 0])
        cap = lbl("slider height = that frequency's arrow length; knob = its rotation", 20
                  ).to_edge(DOWN, buff=1.0)
        p.beat(0.3, lambda rt: self.play(FadeIn(eq, lag_ratio=0.05), FadeIn(cap), run_time=rt / 2))
        # split -> sliders -> recombine
        stages = VGroup(lbl("split into frequencies", 22, SIGNAL), lbl("each through its slider and knob", 22, EIGEN),
                        lbl("recombine: the stairwell guitar", 22, STAMP)).arrange(RIGHT, buff=0.8).to_edge(UP, buff=1.2)
        p.beat(0.7, lambda rt: [self.play(FadeIn(s), run_time=rt / 8) for s in stages])
        both = lbl("scene 5's stamping and this EQ: the same operation", 22, STAMP)
        both.next_to(eq, UP, buff=0.8)
        p.beat(0.85, lambda rt: self.play(FadeIn(both), run_time=min(1, rt / 2)))
        yhx = tex(r"Y(\omega)=H(\omega)\,X(\omega)", size=44, color=INK).to_edge(UP, buff=2.2)
        p.beat(1.0, lambda rt: self.play(FadeOut(stages), FadeOut(both), Write(yhx), run_time=min(1.5, rt / 2)))


class Scene08Comb(RoomScene):
    scene_id = "08"

    def construct(self):
        p = self.pacer
        self.add(head("One wall as an EQ: the comb"))
        a, tau = 0.6, 0.010
        ask = lbl("a tone plus its own 10 ms echo, pitch slowly rising: what happens?", 22).to_edge(DOWN, buff=1.0)
        # phasor: long arrow (direct) + short arrow (echo) on its tip
        origin = np.array([-4.2, -0.2, 0])
        f = ValueTracker(0.0)
        def build():
            ang = -2 * np.pi * f.get_value() * tau
            direct = Arrow(origin, origin + [2.0, 0, 0], buff=0, color=SIGNAL, stroke_width=6)
            tip = direct.get_end()
            echo = Arrow(tip, tip + 2.0 * a * np.array([np.cos(ang), np.sin(ang), 0]), buff=0,
                         color=ECHO, stroke_width=6)
            return VGroup(direct, echo)
        arrows = always_redraw(build)
        circ = Circle(radius=2.0 * a, color=GHOST, stroke_width=2).move_to(origin + [2.0, 0, 0])
        ax = Axes(x_range=[0, 300, 100], y_range=[0, 1.8, 1], x_length=6, y_length=2.6,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(RIGHT * 3.0 + UP * 0.2)
        fr = np.linspace(0, 300, 400)
        comb = curve_on(ax, fr, np.sqrt(mc.comb_mag2(2 * np.pi * fr, tau, a)), EIGEN)
        cursor = always_redraw(lambda: Line(ax.c2p(f.get_value(), 0), ax.c2p(f.get_value(), 1.8),
                                            color=STAMP, stroke_width=2))
        fwd = lbl("pointing forward: loud", 18, EIGEN).next_to(circ, UP, buff=0.5)
        back = lbl("pointing backward: near silence", 18, CORAL).next_to(circ, DOWN, buff=0.5)
        p.beat(0.2, lambda rt: self.play(FadeIn(ask), run_time=min(1, rt / 3)))
        p.beat(0.35, lambda rt: self.play(Transform(ask, lbl("it nearly vanishes at certain pitches", 24, CORAL
                                                             ).to_edge(DOWN, buff=1.0)), run_time=min(1, rt / 2)))
        def setup(rt):
            self.play(Create(circ), FadeIn(arrows), FadeIn(ax), Create(comb), FadeIn(cursor), run_time=rt / 2)
        p.beat(0.5, setup)
        p.beat(0.85, lambda rt: self.play(f.animate.set_value(300), run_time=rt, rate_func=lambda t: t))
        self.play(FadeIn(fwd), FadeIn(back), run_time=0.3)
        notch = VGroup(*[lbl(f"{int(x)} Hz", 16, CORAL).next_to(ax.c2p(x, 0), DOWN, buff=0.12)
                         for x in mc.comb_notch_hz(tau)])
        end = lbl("notches every 100 Hz: flanger, and the hollow sound near a wall. Those notches are sound cancelling itself. Next video.",
                  16, INK_DIM).to_edge(DOWN, buff=1.0)
        p.beat(1.0, lambda rt: self.play(FadeIn(notch), Transform(ask, end), run_time=min(1.5, rt)))


class Scene09Shower(RoomScene):
    scene_id = "09"

    def construct(self):
        p = self.pacer
        self.add(head("Singing in the shower"))
        ax = Axes(x_range=[0, 300, 100], y_range=[0, 4, 2], x_length=9, y_length=3,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(DOWN * 0.1)
        fs = np.linspace(20, 300, 12)
        h = np.array([3.4, 0.7, 0.5, 2.8, 0.6, 0.5, 2.2, 0.8, 0.6, 1.8, 0.7, 0.5])
        eq, _ = sliders(h / 4, width=8, height=2.8)
        eq.move_to(ax.get_center() + DOWN * 0.0)
        cap = lbl("low end of a real room's EQ: a few tall isolated sliders, a handful of oscillators you can count",
                  18).to_edge(DOWN, buff=1.0)
        p.beat(0.3, lambda rt: self.play(FadeIn(ax), FadeIn(eq, lag_ratio=0.05), FadeIn(cap), run_time=rt / 2))
        # overlay a resonance curve on one peak
        w = np.linspace(0, 300, 300)
        peak = 3.4 / np.sqrt(1 + ((w - 40) / 12) ** 2)
        res = curve_on(ax, w, peak, STAMP)
        sw = lbl("a swing pushed at the right rhythm builds up; at the wrong rhythm, it doesn't", 18, INK
                 ).next_to(ax, UP, buff=0.5)
        fit = lbl("a mass-spring resonance curve fits the peak", 20, STAMP).next_to(res, RIGHT, buff=0.3).shift(UP * 0.3)
        p.beat(0.7, lambda rt: self.play(Create(res), FadeIn(sw), FadeIn(fit), run_time=rt / 2))
        hi = lbl("higher up: too many to tell apart, so it behaves like the noisy tail from scene 4", 18, CORAL
                 ).to_edge(DOWN, buff=1.0)
        p.beat(1.0, lambda rt: self.play(Transform(cap, hi), run_time=min(1, rt / 2)))
