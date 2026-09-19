"""Scene 2 (00:08-00:21) -- The roller coaster.

Goal: distinguish energy *exchange* from accumulated *work*.  The energy bars
and the car are driven from one physical state, never animated independently,
and the work meter is labelled "Work by gravity", not "Energy".
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    Create, Dot, FadeIn, FadeOut, RoundedRectangle, VGroup, ValueTracker,
)
from manim import DOWN, LEFT, RIGHT, UP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from basel.coaster import Coaster  # noqa: E402
from basel.config import CYAN, GOLD, INK, INK_DIM, SMALL_SIZE  # noqa: E402
from basel.helpers import (  # noqa: E402
    BaselScene, ComplexPanel, EnergyBars, WorkMeter, live_number, run_scene,
    small,
)

RIDE_SCREEN_SECONDS = 7.0


def make_stage():
    """Geometry shared by scene 2 and scene 3, so the coaster keeps identity."""
    coaster = Coaster()
    panel = ComplexPanel(centre=LEFT * 1.55 + UP * 0.35, unit=0.95)
    return coaster, panel


def track_mobject(coaster: Coaster, panel: ComplexPanel, samples: int = 3000):
    from manim import VMobject
    u = np.linspace(0.0, 1.0, samples)
    points = panel.c2p_many(coaster._curve(u))
    track = VMobject(color=INK_DIM, stroke_width=3.0)
    track.set_points_as_corners(points)
    return track


def build(scene, runner):
    coaster, panel = make_stage()
    track = track_mobject(coaster, panel)

    peak = coaster.point_at(0.0)
    peak_dot = Dot(panel.c2p(peak), radius=0.07, color=GOLD)
    peak_tag = small("A", size=22, color=GOLD).next_to(peak_dot, UP, buff=0.12)

    car = RoundedRectangle(width=0.30, height=0.17, corner_radius=0.05,
                           fill_color=CYAN, fill_opacity=1.0, stroke_width=0)
    car.move_to(panel.c2p(peak))

    bars = EnergyBars(total=coaster.bar_total, height=2.3)
    bars.move_to(RIGHT * 4.6 + UP * 0.55)
    bars.set_state(coaster.potential_at(0.0), coaster.kinetic_at(0.0))

    no_friction = small("No friction or drag", size=20, color=INK_DIM)
    no_friction.next_to(track, DOWN, buff=0.28).shift(LEFT * 0.2)

    speed_tag = small("speed", size=18, color=CYAN)
    speed_readout = live_number(float(coaster.speed_at(0.0)), places=2,
                                size=SMALL_SIZE, color=CYAN)
    speed_group = VGroup(speed_tag, speed_readout).arrange(RIGHT, buff=0.16)
    speed_group.next_to(bars, DOWN, buff=0.5)

    # ---- 00:08-00:11  build the track --------------------------------------
    def beat_one():
        scene.play(Create(track), run_time=1.25)
        scene.play(FadeIn(peak_dot, scale=0.6), FadeIn(peak_tag),
                   FadeIn(car, scale=0.7), FadeIn(no_friction), run_time=0.6)
        scene.play(FadeIn(bars), FadeIn(speed_group), run_time=0.55)

    runner.run("build_track", beat_one)

    # ---- 00:11-00:18  one complete ride, A back to A -----------------------
    clock = ValueTracker(0.0)
    state = {"angle": 0.0}

    def arc_now():
        return float(coaster.arc_length_at_time(clock.get_value()))

    # Each mobject carries its own updater.  Driving them all from one other
    # mobject's updater would leave any of them that sits earlier in the scene
    # baked into manim's static frame cache, silently frozen.  They still read
    # the SAME physical state, so the bars can never drift from the car.
    def drive_car(mobject):
        s = arc_now()
        mobject.move_to(panel.c2p(coaster.point_at(s)))
        # Rotate incrementally: rebuilding the car every frame would be waste.
        target = float(np.angle(complex(coaster.tangent_at(s))))
        mobject.rotate(target - state["angle"])
        state["angle"] = target

    def drive_bars(mobject):
        s = arc_now()
        mobject.set_state(float(coaster.potential_at(s)), float(coaster.kinetic_at(s)))

    def drive_speed(mobject):
        mobject.set_value(float(coaster.speed_at(arc_now())))
        mobject.next_to(speed_tag, RIGHT, buff=0.16)

    def beat_two():
        car.add_updater(drive_car)
        bars.add_updater(drive_bars)
        speed_readout.add_updater(drive_speed)
        span = max(runner.left_in("full_ride") - 0.05, 0.5)
        scene.play(clock.animate.set_value(coaster.ride_time),
                   run_time=span, rate_func=lambda t: t)
        for mobject in (car, bars, speed_readout):
            mobject.clear_updaters()

    runner.run("full_ride", beat_two)

    # ---- 00:18-00:21  the work meter ---------------------------------------
    def beat_three():
        car.move_to(panel.c2p(coaster.point_at(0.0)))
        bars.set_state(float(coaster.potential_at(0.0)), float(coaster.kinetic_at(0.0)))
        speed_readout.set_value(float(coaster.speed_at(0.0)))
        speed_readout.next_to(speed_tag, RIGHT, buff=0.16)

        meter = WorkMeter(span=3.4, width=2.6)
        meter.next_to(bars, DOWN, buff=1.05).align_to(bars, RIGHT).shift(RIGHT * 0.1)
        along_note = small("push along the track", size=18, color=INK_DIM)
        along_note.next_to(meter, DOWN, buff=0.16)

        scene.play(FadeIn(meter), FadeIn(along_note), run_time=0.5)

        # Replay the ride as a short trace; the work returns to zero at A.
        trace_clock = ValueTracker(0.0)
        tracer = Dot(panel.c2p(coaster.point_at(0.0)), radius=0.055, color=GOLD)

        def follow(mobject):
            s = float(coaster.arc_length_at_time(trace_clock.get_value()))
            mobject.move_to(panel.c2p(coaster.point_at(s)))

        tracer.add_updater(follow)
        meter.add_updater(lambda m: m.set_work(float(coaster.work_at(
            float(coaster.arc_length_at_time(trace_clock.get_value()))))))
        scene.add(tracer)
        span = max(runner.left_in("work_meter") - 0.25, 0.4)
        scene.play(trace_clock.animate.set_value(coaster.ride_time),
                   run_time=span, rate_func=lambda t: t)
        tracer.clear_updaters()
        meter.clear_updaters()
        meter.set_work(0.0)
        scene.play(FadeOut(tracer), run_time=0.18)

    runner.run("work_meter", beat_three)


class Scene02Coaster(BaselScene):
    scene_id = "02"

    def construct(self):
        run_scene(self, "02", build)
