"""Scene 4 (00:31-00:47) -- Complex accumulation: along and across.

Goal: the integral is an accumulated complex displacement whose two coordinates
are circulation and flux.  Every contribution asks two questions at once: how
hard does the flow push *along* the path, and how much leaks *across* it.

The fluid on screen is conj(f).  The product that forms each contribution uses
f.  The flip between them is shown explicitly, never assumed.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    Circle, Create, Dot, FadeIn, FadeOut, Line, VGroup, VMobject, ValueTracker,
)
from manim import DOWN, LEFT, RIGHT, UP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from basel.config import (  # noqa: E402
    CYAN, GOLD, INK, INK_DIM, SLATE, SLATE_DIM, SMALL_SIZE,
)
from basel.flux import FlowField, ParticleLayer, flow_caption  # noqa: E402
from basel.helpers import (  # noqa: E402
    BaselScene, ComplexPanel, ContributionChain, dashed_arrow, eq, live_number,
    run_scene, small, solid_arrow,
)
from basel.mathcore import (  # noqa: E402
    circle_path, f_identity, running_integral_exact_identity,
)

RADIUS = 1.5
FREEZE_ANGLE = np.deg2rad(160.0)     # both along and across are positive here
ZOOM = 3.4


def make_panels(unit: float = 0.85):
    left = ComplexPanel(centre=LEFT * 4.15 + UP * 0.45, unit=unit,
                        half_width=2.15, half_height=1.95, name="Input path")
    right = ComplexPanel(centre=RIGHT * 4.15 + UP * 0.45, unit=unit,
                         half_width=2.15, half_height=1.95,
                         x_label="circulation", y_label="i · flux",
                         name="Accumulated integral")
    return left, right


def build(scene, runner):
    left, right = make_panels()
    path = circle_path(RADIUS, samples=1441, start=0.0)
    chain_samples = running_integral_exact_identity(path)   # exact: (z^2-z0^2)/2

    contour = VMobject(color=CYAN, stroke_width=3.2)
    contour.set_points_as_corners(left.c2p_many(path))

    field = FlowField.of(left, f_identity, x_range=(-2.0, 2.0), y_range=(-1.8, 1.8),
                         step=0.5, arrow_scale=0.42)
    particles = ParticleLayer(left, f_identity, count=60, steps=900, dt=0.012,
                              bounds=2.3, seed=5)
    flow_tag = flow_caption()
    flow_tag.next_to(left.axes, UP, buff=0.12).shift(RIGHT * 0.2)

    point = Dot(left.c2p(path[0]), radius=0.075, color=CYAN)
    angle = ValueTracker(0.0)

    def z_of(theta):
        return RADIUS * np.exp(1j * theta)

    point.add_updater(lambda m: m.move_to(left.c2p(z_of(angle.get_value()))))

    # ---- 00:31-00:34  two panels, the contour, and the fluid ---------------
    def beat_one():
        scene.add(field, particles, flow_tag)
        field.set_opacity(0.0)
        particles.set_opacity(0.0)
        flow_tag.set_opacity(0.0)
        scene.play(Create(left.group), Create(right.group), run_time=0.6)
        scene.play(Create(contour), run_time=0.5)
        scene.play(field.animate.set_opacity(0.32),
                   particles.animate.set_opacity(0.55),
                   flow_tag.animate.set_opacity(1.0), run_time=0.45)
        particles.start(speed=0.7)
        scene.add(point)
        scene.play(angle.animate.set_value(FREEZE_ANGLE),
                   run_time=max(runner.left_in("two_panels") - 0.05, 0.3),
                   rate_func=lambda t: t)

    runner.run("two_panels", beat_one)

    # ---- 00:34-00:38  two questions at one step ----------------------------
    z0 = z_of(FREEZE_ANGLE)
    tangent = 1j * np.exp(1j * FREEZE_ANGLE)          # counterclockwise travel
    right_of_travel = -1j * tangent                    # outward on this loop
    flow_here = np.conj(f_identity(z0))
    along_value = float(flow_here.real * tangent.real + flow_here.imag * tangent.imag)
    across_value = float(flow_here.real * tangent.imag - flow_here.imag * tangent.real)

    inset_centre = np.array([0.0, 0.55, 0.0])
    inset_radius = 1.35
    window = Circle(radius=inset_radius, color=INK_DIM, stroke_width=1.8)
    window.move_to(inset_centre)
    marker = Circle(radius=inset_radius / ZOOM * 0.85, color=INK_DIM,
                    stroke_width=1.4).move_to(left.c2p(z0))

    def inset(w):
        """Map an input-plane point into the magnified window."""
        delta = complex(w) - z0
        return inset_centre + np.array([delta.real, delta.imag, 0.0]) * left.unit * ZOOM

    # Kept short enough that the magnified step stays inside the window.
    reach = inset_radius / (left.unit * ZOOM)
    fence = Line(inset(z0 - tangent * reach * 0.94),
                 inset(z0 + tangent * reach * 0.94),
                 color=CYAN, stroke_width=3.0)
    # Scaled so even the longest of the three arrows stays inside the window.
    draw = 0.9 * inset_radius / (abs(flow_here) * left.unit * ZOOM)
    flow_arrow = solid_arrow(inset(z0), inset(z0 + flow_here * draw),
                             color=SLATE, stroke_width=4.0)
    flow_arrow.set_opacity(0.55)   # the parent arrow, dimmer than its two parts
    flow_tip = small("flow", size=16, color=SLATE)
    flow_tip.next_to(inset(z0 + flow_here * draw), DOWN + LEFT, buff=0.06)
    along_arrow = dashed_arrow(inset(z0), inset(z0 + tangent * along_value * draw),
                               color=INK, stroke_width=3.4)
    across_arrow = solid_arrow(
        inset(z0), inset(z0 + right_of_travel * across_value * draw),
        color=SLATE, stroke_width=3.4)

    # Thin guides closing the rectangle, so "split into two parts" is visible.
    from manim import DashedLine
    guide_a = DashedLine(inset(z0 + tangent * along_value * draw),
                         inset(z0 + flow_here * draw), dash_length=0.06,
                         stroke_width=1.3, color=INK_DIM).set_opacity(0.55)
    guide_b = DashedLine(inset(z0 + right_of_travel * across_value * draw),
                         inset(z0 + flow_here * draw), dash_length=0.06,
                         stroke_width=1.3, color=INK_DIM).set_opacity(0.55)

    along_text = small("along: push, like gravity's work", size=18, color=INK)
    across_text = small("across: leak through the fence", size=18, color=SLATE)
    along_swatch = dashed_arrow(LEFT * 0.22, RIGHT * 0.22, color=INK, stroke_width=3.0)
    across_swatch = solid_arrow(LEFT * 0.22, RIGHT * 0.22, color=SLATE, stroke_width=3.0)
    legend = VGroup(
        VGroup(along_swatch, along_text).arrange(RIGHT, buff=0.16),
        VGroup(across_swatch, across_text).arrange(RIGHT, buff=0.16),
    ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    legend.move_to(inset_centre + DOWN * (inset_radius + 0.62))

    crossed_tag = small("crossed the fence:", size=17, color=SLATE)
    crossed_count = live_number(0, places=0, size=17, color=SLATE)
    counter = VGroup(crossed_tag, crossed_count).arrange(RIGHT, buff=0.12)
    counter.move_to(inset_centre + UP * (inset_radius + 0.3))

    # Three particles that visibly cross the segment, on their own schedule.
    crossers = VGroup()
    schedule = [(0.12, 0.45), (0.40, 0.72), (0.64, 0.95)]
    for _ in schedule:
        crossers.add(Dot(inset_centre, radius=0.05, color=SLATE, fill_opacity=0.9))

    cross_clock = ValueTracker(0.0)

    def cross_update(group):
        u = cross_clock.get_value()
        done = 0
        for dot, (begin, end), offset in zip(group, schedule, (-0.25, 0.0, 0.25)):
            frac = float(np.clip((u - begin) / (end - begin), 0.0, 1.0))
            start_w = z0 + tangent * offset - right_of_travel * 0.30
            stop_w = z0 + tangent * offset + right_of_travel * 0.30
            dot.move_to(inset(start_w + (stop_w - start_w) * frac))
            dot.set_opacity(0.0 if frac <= 0.0 else 0.9)
            if frac >= 1.0:
                done += 1
        crossed_count.set_value(done)

    def beat_two():
        scene.play(FadeIn(marker), FadeIn(window), Create(fence), run_time=0.4)
        scene.play(Create(flow_arrow), FadeIn(flow_tip), run_time=0.35)
        scene.play(Create(along_arrow), Create(across_arrow), FadeIn(legend),
                   FadeIn(guide_a), FadeIn(guide_b), run_time=0.5)
        scene.add(crossers, counter)
        crossers.add_updater(cross_update)
        # The counter owns its own updater: driven from the group's updater it
        # would sit earlier in the scene and render frozen.
        crossed_count.add_updater(lambda m: None)
        scene.play(cross_clock.animate.set_value(1.0),
                   run_time=max(runner.left_in("fence_beat") - 0.05, 0.4),
                   rate_func=lambda t: t)

    runner.run("fence_beat", beat_two)

    # ---- 00:38-00:42  one product answers both -----------------------------
    chain = ContributionChain(right, chain_samples)
    tip = Dot(right.c2p(0), radius=0.06, color=GOLD)

    def beat_three():
        crossers.clear_updaters()
        # Clear the split before the product: three overlapping arrow pairs in
        # one small window is one dominant action too many.
        scene.play(FadeOut(crossers), FadeOut(counter), FadeOut(legend),
                   FadeOut(along_arrow), FadeOut(across_arrow),
                   FadeOut(guide_a), FadeOut(guide_b), run_time=0.25)

        # The step dz, and the conjugated arrow.  conj flips the angle, so the
        # product's angle is the angle between step and flow.
        step_arrow = solid_arrow(inset(z0), inset(z0 + tangent * 0.40),
                                 color=CYAN, stroke_width=3.4)
        step_tag = small("dz", size=17, color=CYAN).next_to(
            step_arrow.get_end(), DOWN, buff=0.08)
        flipped = solid_arrow(inset(z0), inset(z0 + np.conj(flow_here) * draw),
                              color=GOLD, stroke_width=3.4)
        flip_tag = small("f", size=18, color=GOLD).next_to(
            flipped.get_end(), UP, buff=0.08)
        flip_note = small("conjugating flips the angle", size=17, color=GOLD)
        flip_note.move_to(inset_centre + DOWN * (inset_radius + 0.42))

        scene.play(Create(step_arrow), FadeIn(step_tag), run_time=0.4)
        scene.play(Create(flipped), FadeIn(flip_tag), FadeIn(flip_note),
                   run_time=0.4)

        product = eq(r"f(z)\,dz=\big(\text{along}+i\,\text{across}\big)\,|dz|",
                     size=26, color=INK).move_to(DOWN * 2.16)
        summed = eq(r"\oint_C f(z)\,dz=\text{circulation}+i\cdot\text{flux}",
                    size=26, color=INK).move_to(DOWN * 2.66)
        scene.play(FadeIn(product), run_time=0.22)
        scene.play(FadeIn(summed), run_time=0.22)

        scene.add(chain, tip)
        fraction = FREEZE_ANGLE / (2 * np.pi)
        progress = ValueTracker(0.0)
        chain.add_updater(lambda m: (m.show_fraction(progress.get_value() * fraction),
                                     None)[1])
        tip.add_updater(lambda m: m.move_to(chain.points_cache[max(
            1, int(progress.get_value() * fraction * (len(chain.points_cache) - 1)))]))
        scene.play(progress.animate.set_value(1.0),
                   run_time=max(runner.left_in("one_product") - 0.05, 0.3),
                   rate_func=lambda t: t)
        scene.remove(step_arrow, step_tag, flipped, flip_tag, flip_note)
        scene._s04_product = VGroup(product, summed)

    runner.run("one_product", beat_three)

    # ---- 00:42-00:45  finish the loop; both totals return to zero ----------
    def beat_four():
        scene.play(FadeOut(window), FadeOut(fence), FadeOut(flow_arrow),
                   FadeOut(flow_tip), FadeOut(marker), run_time=0.25)

        chain.clear_updaters()
        tip.clear_updaters()
        total = ValueTracker(FREEZE_ANGLE / (2 * np.pi))
        chain.add_updater(lambda m: m.show_fraction(total.get_value()))
        tip.add_updater(lambda m: m.move_to(chain.points_cache[max(
            1, int(total.get_value() * (len(chain.points_cache) - 1)))]))
        angle.clear_updaters()
        point.add_updater(lambda m: m.move_to(
            left.c2p(z_of(total.get_value() * 2 * np.pi))))

        span = max(runner.left_in("close_the_loop") - 0.85, 0.4)
        scene.play(total.animate.set_value(1.0), run_time=span,
                   rate_func=lambda t: t)
        chain.clear_updaters()
        tip.clear_updaters()
        point.clear_updaters()

        # Short enough to sit beside the origin without reaching the frame edge
        # or colliding with the "circulation" axis label.
        zero_tag = small("back to 0", size=17, color=GOLD)
        zero_tag.next_to(right.c2p(0), DOWN + RIGHT, buff=0.12).shift(DOWN * 0.24)

        cauchy = eq(r"\oint_C f(z)\,dz = 0", size=30, color=GOLD)
        cauchy.move_to(DOWN * 2.02)
        condition = small("Analytic on and inside the loop", size=18, color=INK_DIM)
        condition.next_to(cauchy, DOWN, buff=0.14)
        translation = small("no faucets, no whirlpools inside", size=18, color=SLATE)
        translation.next_to(condition, DOWN, buff=0.08)

        scene.play(FadeOut(scene._s04_product), run_time=0.15)
        scene.play(FadeIn(zero_tag), FadeIn(cauchy), FadeIn(condition),
                   FadeIn(translation), run_time=0.45)
        scene._s04_tail = VGroup(zero_tag, cauchy, condition, translation)

    runner.run("close_the_loop", beat_four)

    # ---- 00:45-00:47  shrink the contour; the endpoint stays at zero -------
    def beat_five():
        # The chain is recomputed for each contour: its shape changes, its
        # final displacement does not.  The camera never moves.
        shrink = ValueTracker(1.0)

        def reshape_contour(mobject):
            scale = shrink.get_value()
            mobject.set_points_as_corners(left.c2p_many(path * scale))

        def reshape_chain(mobject):
            scale = shrink.get_value()
            mobject.points_cache = right.c2p_many(chain_samples * scale**2)
            mobject.show_fraction(1.0)

        contour.add_updater(reshape_contour)
        chain.add_updater(reshape_chain)
        point.add_updater(lambda m: m.move_to(left.c2p(path[0] * shrink.get_value())))
        tip.add_updater(lambda m: m.move_to(right.c2p(0)))
        scene.play(shrink.animate.set_value(0.08),
                   run_time=max(runner.left_in("shrink") - 0.05, 0.3),
                   rate_func=lambda t: t)
        for mobject in (contour, chain, point, tip):
            mobject.clear_updaters()

    runner.run("shrink", beat_five)


class Scene04Accumulation(BaselScene):
    scene_id = "04"

    def construct(self):
        run_scene(self, "04", build)
