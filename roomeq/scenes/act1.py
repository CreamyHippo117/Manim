"""Act I -- A room makes copies (scenes 0-3).

Narration is recorded separately; ODE callbacks are SPOKEN, never written.
Math on screen only where the script allows it: scene 1 (delta label) and
scene 2 (the stamp equation).
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, Line,
    Polygon, Rectangle, Text, Transform, VGroup, ValueTracker, Write, always_redraw,
    Arrow,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from roomeq.config import CORAL, ECHO, GHOST, GOLD, INK, INK_DIM, SIGNAL, STAMP, TEAL  # noqa: E402
from roomeq.core import RoomScene, curve_on, head, say, tex  # noqa: E402


def lbl(text, size=22, color=INK_DIM):
    return Text(text, font_size=size, color=color)


class Scene00ColdOpen(RoomScene):
    scene_id = "00"

    def construct(self):
        p = self.pacer
        ax = Axes(x_range=[0, 4, 1], y_range=[-1, 1, 1], x_length=10, y_length=2.6,
                  axis_config={"color": INK_DIM, "stroke_width": 1.5, "include_ticks": False})
        t = np.linspace(0, 4, 700)
        dry = np.exp(-t * 6) * np.sin(2 * np.pi * 9 * t) * 0.9
        wet = np.convolve(dry, np.exp(-np.arange(300) / 60) * 0.12)[:len(t)]
        l1 = lbl("a dry guitar", 28).next_to(ax, UP)
        w1 = curve_on(ax, t, dry, SIGNAL)
        p.beat(0.4, lambda rt: (self.play(FadeIn(ax), FadeIn(l1), run_time=min(1, rt / 4)),
                                self.play(Create(w1), run_time=rt / 2)))
        l2 = lbl("the same guitar, in a stairwell", 28, STAMP).next_to(ax, UP)
        w2 = curve_on(ax, t, wet, STAMP)
        p.beat(0.75, lambda rt: self.play(Transform(l1, l2), Transform(w1, w2), run_time=rt / 2))
        q = say("What did the room do to the guitar?", 28, INK)
        p.beat(1.0, lambda rt: self.play(FadeIn(q), run_time=min(1, rt)))


class Scene01Impulse(RoomScene):
    scene_id = "01"

    def construct(self):
        p = self.pacer
        self.add(head("An impulse is anything faster than the room can notice"))
        ax = Axes(x_range=[-1, 1, 1], y_range=[0, 5.2, 1], x_length=5.5, y_length=3,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(DOWN * 0.4)
        # predict: 1 ms vs 0.3 ms click, same energy
        ask = lbl("1 ms click vs 0.3 ms click, same energy: different in the stairwell?", 22
                  ).to_edge(DOWN, buff=1.0)
        eps = ValueTracker(1.0)
        bump = always_redraw(lambda: Polygon(
            ax.c2p(-eps.get_value() / 2, 0), ax.c2p(-eps.get_value() / 2, 1 / eps.get_value()),
            ax.c2p(eps.get_value() / 2, 1 / eps.get_value()), ax.c2p(eps.get_value() / 2, 0),
            stroke_color=SIGNAL, stroke_width=3, fill_color=SIGNAL, fill_opacity=0.35))
        p.beat(0.25, lambda rt: self.play(FadeIn(ax), FadeIn(bump), FadeIn(ask), run_time=min(1.2, rt / 3)))
        same = lbl("reveal: identical", 26, STAMP).to_edge(DOWN, buff=1.0)
        p.beat(0.4, lambda rt: self.play(Transform(ask, same), run_time=min(1, rt / 2)))
        # squeeze narrower and taller, area fixed, until it becomes an arrow
        arrow = Arrow(ax.c2p(0, 0), ax.c2p(0, 5), buff=0, color=STAMP, stroke_width=6)
        p.beat(0.8, lambda rt: self.play(eps.animate.set_value(0.2), run_time=rt / 2))
        def become(rt):
            self.play(FadeOut(bump), Create(arrow), run_time=rt / 3)
        p.beat(0.9, become)
        delta = tex(r"\delta", size=60, color=STAMP).next_to(arrow, RIGHT, buff=0.3).shift(UP * 0.8)
        p.beat(1.0, lambda rt: self.play(Write(delta), run_time=min(1, rt)))


class Scene02Mirrors(RoomScene):
    scene_id = "02"

    def construct(self):
        p = self.pacer
        self.add(head("Walls are mirrors for sound"))
        wx = 0.5
        wall = Line([wx, -2.2, 0], [wx, 2.0, 0], stroke_width=8, color=INK_DIM)
        src = Dot([-3.0, 0.5, 0], color=SIGNAL, radius=0.1)
        mic = Dot([-3.0, -1.0, 0], color=INK, radius=0.1)
        img = Dot([2 * wx + 3.0, 0.5, 0], color=SIGNAL, radius=0.1, fill_opacity=0.35)
        hit = [wx, -0.15, 0]
        bent = VGroup(Line(src.get_center(), hit, color=ECHO), Line(hit, mic.get_center(), color=ECHO))
        straight = DashedLine(img.get_center(), mic.get_center(), color=ECHO)
        direct = Line(src.get_center(), mic.get_center(), color=SIGNAL)
        names = VGroup(lbl("source", 18).next_to(src, UP, buff=0.1), lbl("mic", 18).next_to(mic, DOWN, buff=0.1),
                       lbl("wall", 18).next_to(wall, UP, buff=0.1))
        def geo(rt):
            self.play(Create(wall), FadeIn(src), FadeIn(mic), FadeIn(names), run_time=rt / 4)
            self.play(Create(direct), Create(bent), run_time=rt / 4)
        p.beat(0.2, geo)
        p.beat(0.35, lambda rt: self.play(FadeIn(img), Transform(bent, straight), run_time=rt / 2))
        extra = lbl("the leftover length glows", 18, ECHO).next_to(straight, DOWN, buff=0.2)
        num = lbl("3.4 m extra at 340 m/s = 10 ms", 28, INK).to_edge(RIGHT, buff=0.6).shift(UP * 2)
        p.beat(0.5, lambda rt: self.play(FadeIn(extra), Write(num), run_time=rt / 2))
        # the stamp lifts off the time axis in its permanent colour
        axh = Axes(x_range=[0, 3, 1], y_range=[0, 1.2, 1], x_length=4.2, y_length=1.5,
                   axis_config={"color": INK_DIM, "include_ticks": False}
                   ).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.8)
        s0 = Line(axh.c2p(0, 0), axh.c2p(0, 1), color=STAMP, stroke_width=7)
        s1 = Line(axh.c2p(1.6, 0), axh.c2p(1.6, 0.6), color=STAMP, stroke_width=7)
        stamp_lbl = lbl("the stamp: h", 22, STAMP).next_to(axh, UP, buff=0.1)
        p.beat(0.7, lambda rt: (self.play(FadeOut(num), FadeIn(axh), run_time=rt / 4),
                                self.play(Create(s0), Create(s1), FadeIn(stamp_lbl), run_time=rt / 3)))
        cap = tex(r"h(t)=\delta(t)+a\,\delta(t-\tau)", size=36, color=STAMP).next_to(axh, DOWN, buff=0.4)
        p.beat(1.0, lambda rt: self.play(Write(cap), run_time=min(1.5, rt / 2)))


class Scene03Dont(RoomScene):
    scene_id = "03"

    def construct(self):
        p = self.pacer
        self.add(head("The room doesn't care"))
        ax = Axes(x_range=[0, 6, 1], y_range=[-1.5, 1.5, 1], x_length=6, y_length=2.2,
                  axis_config={"color": INK_DIM, "include_ticks": False}).shift(LEFT * 3.4 + UP * 0.6)
        xs = np.linspace(0, 6, 300)
        c1 = np.exp(-((xs - 1.5) / 0.15) ** 2)
        c2 = np.exp(-((xs - 2.0) / 0.15) ** 2) * 0.9
        total = c1 + c2
        dashed_sum = curve_on(ax, xs, total, GHOST, 2)
        clip_out = curve_on(ax, xs, np.clip(1.6 * total, -1, 1) / 1.6, CORAL)
        room_out = curve_on(ax, xs, total, SIGNAL)
        clip_l = lbl("clipper: the together output is not the sum", 20, CORAL).next_to(ax, DOWN)
        room_l = lbl("room: lands exactly on the dashed sum", 20, SIGNAL).next_to(ax, DOWN)
        pred = lbl("two claps, separate then together: just the two outputs added?", 20).to_edge(DOWN, buff=1.0)
        p.beat(0.2, lambda rt: self.play(FadeIn(ax), FadeIn(dashed_sum), FadeIn(pred), run_time=min(1, rt / 2)))
        p.beat(0.45, lambda rt: (self.play(Create(clip_out), FadeIn(clip_l), run_time=rt / 3)))
        p.beat(0.6, lambda rt: self.play(Transform(clip_out, room_out), Transform(clip_l, room_l), run_time=rt / 2))
        # clap one second later: the output just slides
        slide = curve_on(ax, xs, np.roll(total, 60), STAMP)
        sl = lbl("clap later: the output just slides", 20, STAMP).next_to(room_l, DOWN, buff=0.15)
        p.beat(0.78, lambda rt: self.play(Transform(clip_out, slide), FadeIn(sl), run_time=rt / 2))
        w1 = lbl("doesn't care how loud", 34, INK).to_edge(RIGHT, buff=0.8).shift(UP * 1.2)
        w1b = lbl("linear", 28, TEAL).next_to(w1, DOWN, buff=0.15, aligned_edge=LEFT)
        w2 = lbl("doesn't care when", 34, INK).next_to(w1b, DOWN, buff=0.8, aligned_edge=LEFT)
        w2b = lbl("time-invariant", 28, TEAL).next_to(w2, DOWN, buff=0.15, aligned_edge=LEFT)
        p.beat(1.0, lambda rt: (self.play(Write(w1), FadeIn(w1b), run_time=rt / 4),
                                self.play(Write(w2), FadeIn(w2b), run_time=rt / 4)))
