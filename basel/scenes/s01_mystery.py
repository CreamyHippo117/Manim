"""Scene 1 (00:00-00:08) -- The mystery.

Make the sum feel concrete before any machinery arrives.  No complex plane yet.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import Dot, FadeIn, FadeOut, Line, NumberLine, ValueTracker, Write
from manim import DOWN, LEFT, RIGHT, UP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from basel.config import CYAN, GOLD, INK, INK_DIM, SMALL_SIZE  # noqa: E402
from basel.helpers import (  # noqa: E402
    BaselScene, eq, label, live_number, run_scene, small,
)

TARGET = float(np.pi**2 / 6)


def _partial(n: int) -> float:
    return float(sum(1.0 / k**2 for k in range(1, n + 1)))


def build(scene, runner):
    # ---- 00:00-00:02  the first four terms, and a number line -------------
    terms = eq(r"1", r"+\frac{1}{4}", r"+\frac{1}{9}", r"+\frac{1}{16}",
               r"+\cdots", size=52)
    terms.move_to(UP * 1.55)

    line = NumberLine(x_range=[0, 1.8, 0.2], length=9.6, include_numbers=True,
                      font_size=20, color=INK_DIM, decimal_number_config={
                          "num_decimal_places": 1})
    line.move_to(DOWN * 0.9)
    line.numbers.set_color(INK_DIM)

    def to_x(value: float):
        return line.n2p(float(np.clip(value, 0, 1.8)))

    marker = Dot(to_x(0.0), radius=0.085, color=CYAN)

    # One tracker drives both the dot and the readout, and the readout is set
    # discretely each frame.  Animating a DecimalNumber's value directly would
    # interpolate its glyphs as shapes and smear the digits together.
    sum_tracker = ValueTracker(0.0)
    readout = live_number(0.0, places=4, color=CYAN)

    def follow(mobject):
        value = sum_tracker.get_value()
        mobject.set_value(value)
        mobject.next_to(to_x(value), UP, buff=0.26)

    readout.add_updater(follow)
    marker.add_updater(lambda m: m.move_to(to_x(sum_tracker.get_value())))

    target_tick = Line(DOWN * 0.22, UP * 0.22, stroke_width=3.2, color=GOLD)
    target_tick.move_to(to_x(TARGET))
    # Sits below the axis numbers so it never stacks on top of them.
    target_tag = small("1.644934...", color=GOLD)
    target_tag.next_to(target_tick, DOWN, buff=0.62)

    def beat_one():
        scene.play(FadeIn(terms[0:4], shift=UP * 0.12), run_time=0.7)
        scene.play(FadeIn(line, shift=UP * 0.1), FadeIn(marker, scale=0.6),
                   FadeIn(readout), run_time=0.7)

    runner.run("terms_and_line", beat_one)

    # ---- 00:02-00:05  add terms in batches, advance to real partial sums --
    def beat_two():
        scene.play(FadeIn(terms[4]), FadeIn(target_tick), FadeIn(target_tag),
                   run_time=0.45)

        # The dot lands on actual partial sums -- it is never snapped to pi^2/6.
        batches = [1, 2, 3, 4, 6, 10, 20, 60]
        steps = len(batches)
        start = runner.elapsed()
        span = max(runner.left_in("partial_sums") - 0.1, 0.4)
        # Aim each step at an absolute target time, so frame quantisation
        # self-corrects instead of accumulating across the eight steps.
        for index, count in enumerate(batches):
            target = start + span * (index + 1) / steps
            scene.play(sum_tracker.animate.set_value(_partial(count)),
                       run_time=max(target - runner.elapsed(), 1e-3),
                       rate_func=lambda t: t)

    runner.run("partial_sums", beat_two)

    # ---- 00:05-00:08  reveal pi^2/6 and hold the question -----------------
    def beat_three():
        answer = eq(r"\frac{\pi^2}{6}", size=46, color=GOLD)
        answer.next_to(target_tick, UP, buff=0.55)
        scene.play(Write(answer), run_time=0.7)

        question = label("Why π?", size=40, color=INK).move_to(UP * 0.45)
        scene.play(FadeIn(question, scale=0.85), run_time=0.45)
        scene.wait(1.0)

        # Hand the number line to the coaster scene as a pale horizontal guide,
        # and keep the equation only as a small corner reminder.
        reminder = eq(r"\sum \frac{1}{n^2}=\frac{\pi^2}{6}", size=26, color=INK_DIM)
        reminder.to_corner(UP + LEFT, buff=0.5)
        guide = Line(LEFT * 6.0, RIGHT * 6.0, stroke_width=1.2, color=INK_DIM)
        guide.set_opacity(0.28).move_to(DOWN * 0.9)

        readout.clear_updaters()
        marker.clear_updaters()
        scene.play(
            FadeOut(question), FadeOut(terms), FadeOut(marker), FadeOut(readout),
            FadeOut(target_tag), FadeOut(target_tick), FadeOut(answer),
            FadeOut(line, target_position=guide.get_center()),
            FadeIn(guide), FadeIn(reminder),
            run_time=min(0.8, max(runner.left_in("why_pi") - 0.05, 0.2)),
        )
        scene.remove(reminder)

    runner.run("why_pi", beat_three)


class Scene01Mystery(BaselScene):
    scene_id = "01"

    def construct(self):
        run_scene(self, "01", build)
