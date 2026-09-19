"""Scene 3 (00:21-00:31) -- Path independence.

Goal: the endpoints determine gravity's work.  The two routes are traversed at
their own physical speeds under one common playback acceleration, so they do
not arrive together -- and that is the point worth seeing.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    Create, DashedVMobject, Dot, FadeIn, FadeOut, Transform, VGroup, VMobject,
    ValueTracker, Write,
)
from manim import DOWN, LEFT, RIGHT, UP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from basel.coaster import Coaster, TwoRoutes  # noqa: E402
from basel.config import CYAN, GOLD, INK, INK_DIM, SMALL_SIZE  # noqa: E402
from basel.helpers import (  # noqa: E402
    BaselScene, ComplexPanel, WorkMeter, eq, live_number, run_scene, small,
)
from basel.scenes.s02_coaster import track_mobject  # noqa: E402

ROUTE_STYLE = {"solid": INK_DIM, "dashed": INK_DIM}


def route_mobject(routes: TwoRoutes, panel: ComplexPanel, name: str):
    curve = VMobject(color=CYAN, stroke_width=3.2)
    curve.set_points_as_corners(panel.c2p_many(routes.points(name)))
    if name == "dashed":
        return DashedVMobject(curve, num_dashes=54, color=CYAN, stroke_width=3.2)
    return curve


def _traced_point(routes: TwoRoutes, phase: float):
    """Out along the solid route (phase 0->1), back along the dashed one (1->2).

    This is an abstract tracing dot following a mathematical path, not a second
    physical ride: the return leg runs the dashed route backwards.
    """
    if phase <= 1.0:
        return routes.point_at_time("solid", phase * routes.travel_time("solid"))
    back = 2.0 - phase
    return routes.point_at_time("dashed", back * routes.travel_time("dashed"))


def build(scene, runner):
    routes = TwoRoutes()
    panel = ComplexPanel(centre=LEFT * 1.35 + UP * 0.55, unit=0.80)

    solid = route_mobject(routes, panel, "solid")
    dashed = route_mobject(routes, panel, "dashed")

    a_dot = Dot(panel.c2p(routes.a), radius=0.075, color=GOLD)
    b_dot = Dot(panel.c2p(routes.b), radius=0.075, color=GOLD)
    a_tag = small("A", size=22, color=GOLD).next_to(a_dot, UP, buff=0.12)
    b_tag = small("B", size=22, color=GOLD).next_to(b_dot, DOWN, buff=0.12)

    # ---- 00:21-00:23  morph the closed track into two routes A -> B --------
    def beat_one():
        coaster = Coaster()
        old_panel = ComplexPanel(centre=LEFT * 1.55 + UP * 0.35, unit=0.95)
        track = track_mobject(coaster, old_panel)
        scene.add(track)
        scene.play(Transform(track, solid), run_time=0.85)
        scene.remove(track)
        scene.add(solid)
        scene.play(Create(dashed), FadeIn(a_dot), FadeIn(b_dot),
                   FadeIn(a_tag), FadeIn(b_tag), run_time=0.7)

    runner.run("split_routes", beat_one)

    # ---- 00:23-00:28  release two identical markers -------------------------
    header = small("Shared comparison", size=20, color=INK)
    rows = VGroup()
    entries = {}
    for name in ("solid", "dashed"):
        tag = small("solid route" if name == "solid" else "dashed route",
                    size=19, color=CYAN)
        speed_tag = small("final speed", size=17, color=INK_DIM)
        speed_val = live_number(0.0, places=3, size=17, color=CYAN)
        work_tag = small("work by gravity", size=17, color=INK_DIM)
        work_val = live_number(0.0, places=3, size=17, color=GOLD)
        block = VGroup(
            tag,
            VGroup(speed_tag, speed_val).arrange(RIGHT, buff=0.14),
            VGroup(work_tag, work_val).arrange(RIGHT, buff=0.14),
        ).arrange(DOWN, buff=0.11, aligned_edge=LEFT)
        entries[name] = (speed_val, work_val)
        rows.add(block)
    rows.arrange(DOWN, buff=0.36, aligned_edge=LEFT)
    panel_group = VGroup(header, rows).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
    panel_group.move_to(RIGHT * 4.55 + UP * 0.6)

    markers = {name: Dot(panel.c2p(routes.a), radius=0.075, color=CYAN)
               for name in ("solid", "dashed")}

    def beat_two():
        scene.play(FadeIn(panel_group), FadeIn(markers["solid"]),
                   FadeIn(markers["dashed"]), run_time=0.4)

        span = max(runner.left_in("race") - 0.55, 0.6)
        slowest = max(routes.travel_time(n) for n in ("solid", "dashed"))
        rate = slowest / span          # one common playback acceleration
        clock = ValueTracker(0.0)

        # Arrival snapshots exist from the start at zero opacity, so nothing is
        # constructed mid-play and neither tag can be lost to the frame cache.
        snapshots = {}
        for index, name in enumerate(("solid", "dashed")):
            tag = small(f"{name} route arrives", size=17, color=GOLD)
            tag.next_to(b_dot, DOWN, buff=0.38).shift(DOWN * 0.32 * index)
            tag.set_opacity(0.0)
            snapshots[name] = tag
            scene.add(tag)

        def elapsed(name):
            """Physical seconds travelled on this route, capped at arrival."""
            return min(clock.get_value() * rate, routes.travel_time(name))

        # Every live mobject carries its own updater: a readout driven from
        # another mobject's updater would be baked static and never refresh.
        def bind(name):
            speed_val, work_val = entries[name]
            markers[name].add_updater(
                lambda m, n=name: m.move_to(panel.c2p(
                    routes.point_at_time(n, elapsed(n)))))
            speed_val.add_updater(
                lambda m, n=name: m.set_value(float(
                    routes.speed_at_time(n, elapsed(n)))))
            work_val.add_updater(
                lambda m, n=name: m.set_value(float(
                    routes.a.imag - routes.point_at_time(n, elapsed(n)).imag)))
            snapshots[name].add_updater(
                lambda m, n=name: m.set_opacity(
                    1.0 if clock.get_value() * rate >= routes.travel_time(n) else 0.0))

        for name in ("solid", "dashed"):
            bind(name)
        scene.play(clock.animate.set_value(span), run_time=span,
                   rate_func=lambda t: t)
        for name in ("solid", "dashed"):
            markers[name].clear_updaters()
            for mobject in entries[name]:
                mobject.clear_updaters()
            snapshots[name].clear_updaters()
        scene.play(*[FadeOut(tag) for tag in snapshots.values()], run_time=0.2)

    runner.run("race", beat_two)

    # ---- 00:28-00:31  a mathematical path, and the closed loop -------------
    def beat_three():
        scene.play(FadeOut(markers["solid"]), FadeOut(markers["dashed"]),
                   run_time=0.15)

        work_line = eq(r"W_{\text{gravity}} = U(A) - U(B)", size=30, color=INK)
        work_line.move_to(DOWN * 2.35)
        scene.play(Write(work_line), run_time=0.5)

        note = small("a mathematical path, not a second ride", size=18, color=INK_DIM)
        note.next_to(work_line, UP, buff=0.22)

        meter = WorkMeter(span=3.4, width=2.3)
        meter.next_to(panel_group, DOWN, buff=0.55)
        scene.play(FadeIn(meter), FadeIn(note), run_time=0.3)

        # Out along the solid route, back along the dashed one: the two work
        # totals are equal and opposite, so the round trip cancels.
        tracer = Dot(panel.c2p(routes.a), radius=0.06, color=GOLD)
        phase = ValueTracker(0.0)

        def trace(mobject):
            mobject.move_to(panel.c2p(_traced_point(routes, phase.get_value())))

        tracer.add_updater(trace)
        meter.add_updater(lambda m: m.set_work(float(
            routes.a.imag - _traced_point(routes, phase.get_value()).imag)))
        scene.add(tracer)
        span = max(runner.left_in("closed_loop") - 0.75, 0.5)
        scene.play(phase.animate.set_value(2.0), run_time=span,
                   rate_func=lambda t: t)
        tracer.clear_updaters()
        meter.clear_updaters()
        meter.set_work(0.0)

        closed = eq(r"\oint_C \vec{F}_{\text{gravity}} \cdot d\vec{r} = 0",
                    size=32, color=GOLD).move_to(work_line.get_center())
        # Clear the first statement before the second arrives: these are two
        # different statements, not one glyph morphing into another.
        scene.play(FadeOut(work_line), FadeOut(tracer), FadeOut(note),
                   run_time=0.22)
        scene.play(FadeIn(closed), run_time=0.28)

        # The closed route hands itself to scene 4 as a contour.
        contour_note = small("a closed path: a contour", size=18, color=CYAN)
        contour_note.next_to(closed, UP, buff=0.24)
        scene.play(FadeIn(contour_note), run_time=0.22)

    runner.run("closed_loop", beat_three)


class Scene03PathIndependence(BaselScene):
    scene_id = "03"

    def construct(self):
        run_scene(self, "03", build)
