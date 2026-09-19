"""Scene 6 (01:02-01:16) -- Only one local term survives.

Goal: separate a pole from its residue, and a pole from a faucet.  1/z^2 blows
up just as hard as 1/z and leaks nothing at all.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line, Transform, VGroup,
    VMobject, ValueTracker,
)
from manim import DOWN, LEFT, RIGHT, UP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from basel.config import (  # noqa: E402
    CORAL, CYAN, GHOST, GOLD, INK, INK_DIM, SLATE, SMALL_SIZE,
)
from basel.flux import FlowField, ParticleLayer, flow_caption  # noqa: E402
from basel.helpers import (  # noqa: E402
    BaselScene, ContributionChain, eq, pole_marker, run_scene, small,
    solid_arrow,
)
from basel.mathcore import circle_path, f_inverse_sq  # noqa: E402
from basel.scenes.s04_accumulation import make_panels  # noqa: E402

RADIUS = 0.95
POLES = (-1.55 + 0.15j, 0.85 + 1.05j, 1.35 - 0.95j)


def build(scene, runner):
    left, right = make_panels()
    path = circle_path(RADIUS, samples=1441)
    # Exact primitive of 1/z^2 is -1/z, so the chain is never guessed.
    chain_samples = 1.0 / path[0] - 1.0 / path

    contour = VMobject(color=CYAN, stroke_width=3.2)
    contour.set_points_as_corners(left.c2p_many(path))
    pole_dot = pole_marker(left, 0)
    pole_tag = small("Pole", size=18, color=CORAL)
    pole_tag.next_to(left.c2p(-1.75j), DOWN, buff=0.06)

    fn_label = eq(r"f(z)=\frac{1}{z^2}", size=30, color=INK)
    fn_label.move_to(np.array([-5.55, 3.15, 0.0]))

    field = FlowField.of(left, f_inverse_sq, x_range=(-2.0, 2.0),
                         y_range=(-1.8, 1.8), step=0.5, arrow_scale=0.42,
                         poles=(0,), pole_radius=0.5)
    particles = ParticleLayer(left, f_inverse_sq, count=55, steps=900, dt=0.010,
                              poles=(0,), pole_radius=0.30, bounds=2.3, seed=17)
    flow_tag = flow_caption("Flow = conj(f)")
    flow_tag.next_to(left.axes, UP, buff=0.12).shift(RIGHT * 0.2)

    chain = ContributionChain(right, chain_samples)
    tip = Dot(right.c2p(0), radius=0.055, color=GOLD)

    # ---- 01:02-01:07  the dipole: blows up, but does not leak --------------
    def beat_one():
        scene.add(left.group, right.group)
        scene.play(FadeIn(left.group), FadeIn(right.group), FadeIn(fn_label),
                   FadeIn(contour), FadeIn(pole_dot), FadeIn(pole_tag),
                   run_time=0.5)
        scene.add(field, particles)
        scene.bring_to_back(particles)
        scene.bring_to_back(field)
        particles.start(speed=0.85)
        scene.play(FadeIn(field), FadeIn(particles), FadeIn(flow_tag),
                   run_time=0.45)

        # On the circle the outward component runs like cos t.
        out_tag = small("out", size=16, color=SLATE)
        out_tag.next_to(left.c2p(RADIUS), RIGHT, buff=0.1)
        in_tag = small("in", size=16, color=SLATE)
        in_tag.next_to(left.c2p(-RADIUS), LEFT, buff=0.1)
        scene.play(FadeIn(out_tag), FadeIn(in_tag), run_time=0.3)

        point = Dot(left.c2p(path[0]), radius=0.07, color=CYAN)
        turn = ValueTracker(0.0)
        point.add_updater(lambda m: m.move_to(
            left.c2p(RADIUS * np.exp(1j * turn.get_value()))))
        scene.add(point, chain, tip)
        chain.add_updater(lambda m: m.show_fraction(turn.get_value() / (2 * np.pi)))
        tip.add_updater(lambda m: m.move_to(chain.points_cache[max(
            1, int(turn.get_value() / (2 * np.pi) * (len(chain.points_cache) - 1)))]))
        span = max(runner.left_in("dipole") - 0.75, 0.4)
        scene.play(turn.animate.set_value(2 * np.pi), run_time=span,
                   rate_func=lambda t: t)
        for mobject in (point, chain, tip):
            mobject.clear_updaters()

        zero_tag = small("Integral = 0", size=17, color=GOLD)
        zero_tag.next_to(right.c2p(0), DOWN + RIGHT, buff=0.12).shift(DOWN * 0.2)
        caption = small("Blows up, but doesn't leak", size=19, color=SLATE)
        caption.move_to(DOWN * 2.35)
        scene.play(FadeIn(zero_tag), FadeIn(caption), run_time=0.4)
        scene._s06_clear = VGroup(point, zero_tag, caption, out_tag, in_tag)

    runner.run("dipole", beat_one)

    # ---- 01:07-01:11  three local terms; only one survives -----------------
    def beat_two():
        particles.stop()
        scene.play(FadeOut(scene._s06_clear), FadeOut(field), FadeOut(particles),
                   FadeOut(contour), FadeOut(chain), FadeOut(tip),
                   FadeOut(flow_tag), FadeOut(pole_tag), FadeOut(pole_dot),
                   FadeOut(fn_label), FadeOut(left.group), FadeOut(right.group),
                   run_time=0.3)

        rows = VGroup()
        specs = [
            (r"\frac{a_{-2}}{z^2}", "loop", INK_DIM),
            (r"\frac{a_{-1}}{z}", "up", GOLD),
            (r"a_0", "loop", INK_DIM),
        ]
        for tex, kind, colour in specs:
            term = eq(tex, size=34, color=colour)
            if kind == "loop":
                preview = Circle(radius=0.26, color=colour, stroke_width=2.6)
                result = small("adds to 0", size=16, color=colour)
            else:
                preview = solid_arrow(DOWN * 0.26, UP * 0.26, color=colour,
                                      stroke_width=3.2)
                result = small("adds to 2πi", size=16, color=colour)
            rows.add(VGroup(term, preview, result).arrange(RIGHT, buff=0.5))
        rows.arrange(DOWN, buff=0.52, aligned_edge=LEFT)
        rows.move_to(LEFT * 2.6 + UP * 0.45)

        scene.play(FadeIn(rows), run_time=0.6)
        residue_tag = small("Residue", size=20, color=GOLD)
        residue_tag.next_to(rows[1][0], LEFT, buff=0.4)
        arrow = solid_arrow(residue_tag.get_right() + RIGHT * 0.05,
                            rows[1][0].get_left() + LEFT * 0.05,
                            color=GOLD, stroke_width=2.6)
        scene.play(FadeIn(residue_tag), Create(arrow), run_time=0.35)

        # The fluid dictionary, beside the terms rather than under them.
        dictionary = VGroup(
            small("Real residue r: a faucet pouring out 2πr", size=18, color=SLATE),
            small("Imaginary residue: a whirlpool", size=18, color=SLATE),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        dictionary.move_to(RIGHT * 3.6 + UP * 0.45)
        scene.play(FadeIn(dictionary), run_time=0.35)
        scene._s06_terms = VGroup(rows, residue_tag, arrow, dictionary)

    runner.run("three_local_terms", beat_two)

    # ---- 01:11-01:16  three poles, one total -------------------------------
    def beat_three():
        scene.play(FadeOut(scene._s06_terms), run_time=0.25)

        # A nameless panel here: this beat carries its own caption, and the
        # inherited "Input path" tag would sit on top of it.
        from basel.helpers import ComplexPanel
        wide = ComplexPanel(centre=LEFT * 4.15 + UP * 0.45, unit=0.85,
                            half_width=2.15, half_height=1.95)
        outer = VMobject(color=CYAN, stroke_width=3.0)
        outer.set_points_as_corners(wide.c2p_many(circle_path(2.15, samples=721)))
        dots = VGroup(*[pole_marker(wide, p) for p in POLES])
        scene.play(FadeIn(wide.group), Create(outer), FadeIn(dots), run_time=0.5)

        # Split into three small counterclockwise loops.  The connecting cuts
        # come in pairs traversed both ways, so they cancel -- this is not a
        # topology change waved through without explanation.
        loops = VGroup(*[
            VMobject(color=CYAN, stroke_width=3.0).set_points_as_corners(
                wide.c2p_many(circle_path(0.42, centre=p, samples=361)))
            for p in POLES
        ])
        cuts = VGroup()
        for p in POLES:
            direction = p / abs(p)
            start = wide.c2p(direction * 2.15)
            end = wide.c2p(p + direction * 0.42 * -1)
            for offset in (0.07, -0.07):
                cut = DashedLine(start + np.array([0.0, offset, 0.0]),
                                 end + np.array([0.0, offset, 0.0]),
                                 dash_length=0.08, stroke_width=1.6,
                                 color=INK_DIM).set_opacity(0.78)
                cuts.add(cut)
        cut_tag = small("paired cuts cancel", size=16, color=INK_DIM)
        cut_tag.move_to(wide.centre + DOWN * 2.2)
        scene.play(Create(loops), FadeIn(cuts), FadeIn(cut_tag), run_time=0.7)

        # Each loop hands up one contribution; the three add into one total.
        pieces = VGroup()
        for index, pole in enumerate(POLES):
            arrow = solid_arrow(wide.c2p(pole) + DOWN * 0.1,
                                wide.c2p(pole) + UP * 0.34,
                                color=GOLD, stroke_width=3.0)
            pieces.add(arrow)
        scene.play(FadeIn(pieces), run_time=0.3)

        stack_base = np.array([0.15, -0.55, 0.0])
        targets = VGroup()
        for index in range(len(POLES)):
            start = stack_base + UP * (0.44 * index)
            targets.add(solid_arrow(start, start + UP * 0.44, color=GOLD,
                                    stroke_width=3.0))
        total_tag = small("one total", size=17, color=GOLD)
        total_tag.next_to(targets, UP, buff=0.14)
        scene.play(Transform(pieces, targets), run_time=0.55)
        scene.play(FadeIn(total_tag), run_time=0.2)

        theorem = eq(r"\oint_C f(z)\,dz", r"=", r"2\pi i\sum \operatorname{Res}",
                     size=32, color=GOLD)
        theorem.move_to(RIGHT * 3.9 + UP * 0.6)
        leak = small("the leak through the outer loop is the total of the",
                     size=17, color=SLATE)
        leak2 = small("faucets inside", size=17, color=SLATE)
        note = VGroup(leak, leak2).arrange(DOWN, buff=0.08)
        note.next_to(theorem, DOWN, buff=0.42)
        scene.play(FadeIn(theorem), run_time=0.4)
        scene.play(FadeIn(note), run_time=0.3)

    runner.run("residue_theorem", beat_three)


class Scene06Residues(BaselScene):
    scene_id = "06"

    def construct(self):
        run_scene(self, "06", build)
