"""Scene 5 (00:47-01:02) -- A hole, a sprinkler, and 2 pi i.

Goal: make the nonzero integral of 1/z visible twice over -- as a rotation
cancellation, and as a sprinkler whose leak is 2*pi at every radius.

The accumulation panel's vertical scale is compressed here and *labelled* as
such, because 2*pi does not fit at the scale scene 4 used.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    Circle, Create, Dot, FadeIn, FadeOut, Transform, VGroup, VMobject,
    ValueTracker,
)
from manim import DOWN, LEFT, RIGHT, UP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from basel.config import (  # noqa: E402
    CORAL, CYAN, GHOST, GOLD, INK, INK_DIM, SLATE, SMALL_SIZE,
)
from basel.flux import FlowField, ParticleLayer, flow_caption  # noqa: E402
from basel.helpers import (  # noqa: E402
    BaselScene, ComplexPanel, ContributionChain, eq, run_scene, small,
    solid_arrow,
)
from basel.mathcore import (  # noqa: E402
    circle_path, f_inverse, running_integral_exact_inverse,
)

BIG_R = 0.95
SMALL_R = 0.52
ZOOM_CENTRE = np.array([0.0, 0.5, 0.0])
INSET_RADIUS = 1.25


def make_panels():
    left = ComplexPanel(centre=LEFT * 4.15 + UP * 0.45, unit=0.85,
                        half_width=2.15, half_height=1.95, name="Input path")
    # 2*pi is far taller than scene 4's scale allows, so this panel is
    # compressed -- and says so, rather than quietly lying about the endpoint.
    right = ComplexPanel(centre=RIGHT * 4.15 + DOWN * 1.15, unit=0.26,
                         half_width=2.15, half_height=0.6,
                         x_label="circulation",
                         y_label="i · flux (scale compressed)",
                         name="Accumulated integral",
                         y_span=(-1.2, 7.4), name_below=0.95,
                         y_label_dir=LEFT)
    return left, right


def contour_mobject(panel, radius, color=CYAN, stroke_width=3.2):
    curve = VMobject(color=color, stroke_width=stroke_width)
    curve.set_points_as_corners(panel.c2p_many(circle_path(radius, samples=721)))
    return curve


def build(scene, runner):
    left, right = make_panels()

    # 6i would sit a hair under 2*pi*i and collide with it, so the ticks stop
    # at 4i and the endpoint carries its own gold label.
    ticks = VGroup(right.tick(2j, "2i"), right.tick(4j, "4i"))
    two_pi_tick = right.tick(2j * np.pi, "2πi", color=GOLD)
    scale_note = VGroup()   # the caveat now rides on the axis label itself

    contour = contour_mobject(left, BIG_R)
    puncture = Dot(left.c2p(0), radius=0.085, color=CORAL)
    undefined = small("Undefined", size=17, color=CORAL)
    undefined.next_to(left.c2p(-1.6j), DOWN, buff=0.06)

    # ---- 00:47-00:50  the puncture, and a shrink that has to stop ----------
    def beat_one():
        scene.add(left.group, right.group, ticks, two_pi_tick, scale_note)
        new_f = eq(r"f(z)=\frac{1}{z}", size=30, color=INK)
        new_f.move_to(np.array([-5.55, 3.15, 0.0]))
        scene.play(FadeIn(left.group), FadeIn(right.group), FadeIn(ticks),
                   FadeIn(two_pi_tick), FadeIn(scale_note), FadeIn(new_f),
                   run_time=0.5)
        scene.play(Create(contour), FadeIn(puncture), FadeIn(undefined),
                   run_time=0.5)

        # Try to shrink it away -- and stop short of the puncture.
        radius = ValueTracker(BIG_R)
        contour.add_updater(lambda m: m.set_points_as_corners(
            left.c2p_many(circle_path(radius.get_value(), samples=721))))
        scene.play(radius.animate.set_value(0.30), run_time=0.55,
                   rate_func=lambda t: t)
        scene.play(radius.animate.set_value(BIG_R), run_time=0.45,
                   rate_func=lambda t: t)
        contour.clear_updaters()
        scene._s05_fn = new_f

    runner.run("puncture", beat_one)

    # ---- 00:50-00:53  the conjugate flip: 1/z becomes a sprinkler ----------
    raw_field = FlowField.raw(left, f_inverse, x_range=(-2.0, 2.0),
                              y_range=(-1.8, 1.8), step=0.5, arrow_scale=0.42,
                              poles=(0,), pole_radius=0.42)
    conj_field = FlowField.of(left, f_inverse, x_range=(-2.0, 2.0),
                              y_range=(-1.8, 1.8), step=0.5, arrow_scale=0.42,
                              poles=(0,), pole_radius=0.42)
    particles = ParticleLayer(left, f_inverse, count=60, steps=900, dt=0.012,
                              poles=(0,), pole_radius=0.26, bounds=2.3, seed=11)

    raw_tag = small("plotting f itself: reflected, confusing", size=17, color=INK_DIM)
    raw_tag.next_to(left.axes, UP, buff=0.12).shift(RIGHT * 0.2)
    # One line rather than two stacked labels over the field arrows.
    flow_tag = flow_caption("Flow = conj(f): a sprinkler")
    flow_tag.move_to(raw_tag.get_center())

    def beat_two():
        scene.add(raw_field)
        scene.bring_to_back(raw_field)
        scene.play(FadeIn(raw_field), FadeIn(raw_tag), run_time=0.5)
        # One smooth transformation flips every arrow across the horizontal.
        scene.play(Transform(raw_field, conj_field), FadeOut(raw_tag),
                   FadeIn(flow_tag), run_time=0.85)
        scene.add(particles)
        scene.bring_to_back(particles)
        particles.start(speed=0.9)
        scene.play(FadeIn(particles), run_time=0.4)

    runner.run("conjugate_flip", beat_two)

    # ---- 00:53-00:57  rotation cancellation, and a straight vertical chain --
    path = circle_path(BIG_R, samples=1441)
    chain_samples = running_integral_exact_inverse(path)      # exactly i*t
    chain = ContributionChain(right, chain_samples)
    tip = Dot(right.c2p(0), radius=0.055, color=GOLD)

    window = Circle(radius=INSET_RADIUS, color=INK_DIM, stroke_width=1.8)
    window.move_to(ZOOM_CENTRE)
    turn = ValueTracker(0.0)
    scale = 0.85

    step_arrow = solid_arrow(ZOOM_CENTRE, ZOOM_CENTRE + RIGHT * 0.1,
                             color=CYAN, stroke_width=3.4)
    mult_arrow = solid_arrow(ZOOM_CENTRE, ZOOM_CENTRE + RIGHT * 0.1,
                             color=INK, stroke_width=3.4)
    prod_arrow = solid_arrow(ZOOM_CENTRE, ZOOM_CENTRE + RIGHT * 0.1,
                             color=GOLD, stroke_width=4.0)

    def vec(value):
        value = complex(value)
        return ZOOM_CENTRE + np.array([value.real, value.imag, 0.0]) * scale

    def drive_step(mobject):
        t = turn.get_value()
        mobject.put_start_and_end_on(ZOOM_CENTRE, vec(1j * np.exp(1j * t) * 0.85))

    def drive_mult(mobject):
        t = turn.get_value()
        mobject.put_start_and_end_on(ZOOM_CENTRE,
                                     vec(np.exp(-1j * t) / BIG_R * 0.72))

    def drive_prod(mobject):
        # (1/z) dz is i dt: the product points straight up, always.
        mobject.put_start_and_end_on(ZOOM_CENTRE, vec(1j * 1.0))

    def beat_three():
        scene.play(FadeIn(window), run_time=0.25)
        for mobject, drive in ((step_arrow, drive_step), (mult_arrow, drive_mult),
                               (prod_arrow, drive_prod)):
            drive(mobject)
            mobject.add_updater(drive)
        # Stacked below the window: placed beside it they would reach into
        # the left panel and the accumulation panel.
        step_tag = small("dz turns counterclockwise", size=16, color=CYAN)
        mult_tag = small("1/z turns clockwise", size=16, color=INK)
        tag_stack = VGroup(step_tag, mult_tag).arrange(DOWN, buff=0.1)
        tag_stack.next_to(window, DOWN, buff=0.14)
        prod_tag = small("product: always up", size=16, color=GOLD)
        prod_tag.next_to(window, UP, buff=0.12)
        scene.play(FadeIn(step_arrow), FadeIn(mult_arrow), FadeIn(prod_arrow),
                   FadeIn(step_tag), FadeIn(mult_tag), FadeIn(prod_tag),
                   run_time=0.4)

        identity = eq(r"\frac{1}{z}\,dz = i\,dt", size=28, color=GOLD)
        identity.next_to(tag_stack, DOWN, buff=0.18)
        scene.play(FadeIn(identity), run_time=0.25)

        point = Dot(left.c2p(path[0]), radius=0.07, color=CYAN)
        point.add_updater(lambda m: m.move_to(
            left.c2p(BIG_R * np.exp(1j * turn.get_value()))))
        scene.add(point, chain, tip)
        chain.add_updater(lambda m: m.show_fraction(turn.get_value() / (2 * np.pi)))
        tip.add_updater(lambda m: m.move_to(chain.points_cache[max(
            1, int(turn.get_value() / (2 * np.pi) * (len(chain.points_cache) - 1)))]))

        span = max(runner.left_in("rotation_cancel") - 0.05, 0.4)
        # Constant angular speed: the cancellation only reads if nothing eases.
        scene.play(turn.animate.set_value(2 * np.pi), run_time=span,
                   rate_func=lambda t: t)
        for mobject in (step_arrow, mult_arrow, prod_arrow, chain, tip, point):
            mobject.clear_updaters()
        scene._s05_inset = VGroup(window, step_arrow, mult_arrow, prod_arrow,
                                  step_tag, mult_tag, prod_tag)
        scene._s05_identity = identity
        scene._s05_point = point

    runner.run("rotation_cancel", beat_three)

    # ---- 00:57-01:00  why 2 pi: the r cancels ------------------------------
    def beat_four():
        pure_leak = small("no push along the circle: every contribution is pure leak",
                          size=17, color=SLATE)
        pure_leak.move_to(DOWN * 3.0 + RIGHT * 0.0)
        scene.play(FadeOut(scene._s05_inset), FadeOut(scene._s05_identity),
                   FadeIn(pure_leak), run_time=0.3)

        ghost_ring = contour_mobject(left, BIG_R, color=GHOST, stroke_width=2.0)
        ghost_ring.set_opacity(0.45)
        scene.add(ghost_ring)

        small_path = circle_path(SMALL_R, samples=1441)
        small_chain = ContributionChain(right, running_integral_exact_inverse(small_path))
        small_tip = Dot(right.c2p(0), radius=0.055, color=GOLD)

        radius = ValueTracker(BIG_R)
        contour.add_updater(lambda m: m.set_points_as_corners(
            left.c2p_many(circle_path(radius.get_value(), samples=721))))
        scene.play(radius.animate.set_value(SMALL_R), run_time=0.45,
                   rate_func=lambda t: t)
        contour.clear_updaters()

        why = eq(r"\text{flux}=\frac{1}{r}\cdot 2\pi r = 2\pi",
                 size=28, color=SLATE).move_to(ZOOM_CENTRE + DOWN * 0.35)
        scene.play(FadeIn(why), run_time=0.3)

        scene.remove(chain, tip)
        scene.add(small_chain, small_tip)
        turn2 = ValueTracker(0.0)
        small_chain.add_updater(
            lambda m: m.show_fraction(turn2.get_value() / (2 * np.pi)))
        small_tip.add_updater(lambda m: m.move_to(small_chain.points_cache[max(
            1, int(turn2.get_value() / (2 * np.pi) * (len(small_chain.points_cache) - 1)))]))
        scene._s05_point.add_updater(lambda m: m.move_to(
            left.c2p(SMALL_R * np.exp(1j * turn2.get_value()))))
        span = max(runner.left_in("why_two_pi") - 0.1, 0.4)
        scene.play(turn2.animate.set_value(2 * np.pi), run_time=span,
                   rate_func=lambda t: t)
        for mobject in (small_chain, small_tip, scene._s05_point):
            mobject.clear_updaters()
        scene._s05_why = why
        scene._s05_leak = pure_leak
        scene._s05_ghost = ghost_ring

    runner.run("why_two_pi", beat_four)

    # ---- 01:00-01:02  same faucet inside -----------------------------------
    def beat_five():
        scene.play(FadeOut(scene._s05_why), FadeOut(scene._s05_leak),
                   FadeOut(scene._s05_point), run_time=0.2)

        outer = contour_mobject(left, BIG_R * 1.45)
        inner = contour_mobject(left, SMALL_R * 0.8)
        # The inner mark sits above the inner ring, not on the puncture.
        for ring, where in ((outer, UP * 1.36), (inner, UP * 0.55)):
            arrow_tag = small("↺", size=22, color=CYAN)
            arrow_tag.move_to(left.centre + where)
            ring.add(arrow_tag)
        scene.remove(scene._s05_ghost)
        scene.play(Transform(contour, inner), FadeIn(outer), run_time=0.35)

        statement = eq(r"\oint_{\text{outer}}\frac{dz}{z}",
                       r"=", r"\oint_{\text{inner}}\frac{dz}{z}",
                       r"=", r"0 + i\cdot 2\pi", size=26, color=GOLD)
        statement.move_to(DOWN * 2.75)
        same = small("Same faucet inside", size=18, color=SLATE)
        same.next_to(statement, UP, buff=0.18)
        scene.play(FadeIn(statement), FadeIn(same), run_time=0.4)

    runner.run("same_faucet", beat_five)


class Scene05Sprinkler(BaselScene):
    scene_id = "05"

    def construct(self):
        run_scene(self, "05", build)
