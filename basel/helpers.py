"""Shared building blocks: timing, text, panels, chains, energy bars, markers.

Every scene is built from these, and the assembled overview calls the very same
builder functions the standalone scenes do, so no scene exists twice in two
code paths.
"""

from __future__ import annotations

import numpy as np
from manim import (
    Arrow, Circle, Create, DashedLine, DashedVMobject, DecimalNumber, Dot,
    FadeIn, FadeOut, Line, MathTex, Rectangle, Scene, Text, Transform,
    TransformMatchingTex, VGroup, VMobject, ValueTracker, Write,
)
from manim import DOWN, LEFT, RIGHT, UP, ORIGIN
from manim import config

from .config import (
    BG, CORAL, CYAN, EQUATION_SIZE, GHOST, GOLD, INK, INK_DIM, LABEL_SIZE,
    SAFE_BOTTOM, SAFE_TOP, SMALL_SIZE, SLATE, TEAL, TITLE_SIZE, VIOLET,
    beat_times, scene_duration,
)


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------
class BeatRunner:
    """Runs a scene's named beats and holds each one to its exact end time.

    After a beat's animations finish, the runner pads with a wait so the next
    beat starts on its scheduled boundary.  Drift cannot accumulate: every beat
    is pinned to an absolute time, not to the length of what came before.
    """

    def __init__(self, scene: Scene, scene_id: str, start_time: float | None = None):
        self.scene = scene
        self.scene_id = scene_id
        self.t0 = scene.renderer.time if start_time is None else start_time
        self.spans = {name: (a, b) for name, a, b in beat_times(scene_id)}
        self.duration = scene_duration(scene_id)
        self.overruns: list[tuple[str, float]] = []

    def elapsed(self) -> float:
        return self.scene.renderer.time - self.t0

    def left_in(self, name: str) -> float:
        """Seconds still available inside the named beat."""
        return self.spans[name][1] - self.elapsed()

    def run(self, name: str, body=None):
        _start, end = self.spans[name]
        if body is not None:
            body()
        self._hold_until(end, name)

    def _hold_until(self, end: float, name: str):
        remaining = end - self.elapsed()
        if remaining > 1e-9:
            self.scene.wait(remaining)
        elif remaining < -1e-3:
            self.overruns.append((name, -remaining))
            print(f"[timing] scene {self.scene_id} beat '{name}' overran by "
                  f"{-remaining:.3f}s")

    def finish(self):
        self._hold_until(self.duration, "<scene end>")


class BaselScene(Scene):
    """Base scene: applies the palette, and keeps every duration frame-exact.

    Manim renders ``ceil(run_time * fps)`` frames per animation, so any
    run_time that is not a whole number of frames makes the *written file*
    longer than the scene's internal clock.  At 15 fps those fractions add up
    to seconds across a 120 s film.  Quantising every play and wait to whole
    frames keeps the measured duration equal to the intended one at any frame
    rate, which is what the timing acceptance check actually measures.
    """

    scene_id: str = "00"

    def setup(self):
        self.camera.background_color = BG

    def _whole_frames(self, duration: float, minimum: int = 1) -> float:
        fps = float(config.frame_rate)
        return max(minimum, int(round(float(duration) * fps))) / fps

    def play(self, *args, **kwargs):
        if kwargs.get("run_time") is not None:
            kwargs["run_time"] = self._whole_frames(kwargs["run_time"], minimum=1)
        return super().play(*args, **kwargs)

    def wait(self, duration=1.0, *args, **kwargs):
        snapped = self._whole_frames(duration, minimum=0)
        if snapped <= 0.0:
            return None
        return super().wait(snapped, *args, **kwargs)


def clear_stage(scene: Scene):
    """Drop every mobject and updater so the next scene starts clean.

    Stale updaters and orphaned labels are the main way a long assembled render
    goes wrong, so the overview calls this between scenes.
    """
    for mobject in list(scene.mobjects):
        mobject.clear_updaters()
    if scene.mobjects:
        scene.remove(*scene.mobjects)
    scene.foreground_mobjects = []


def run_scene(scene: Scene, scene_id: str, builder, start_time: float | None = None):
    """Run one scene's builder under its beat map.  Used by both code paths."""
    runner = BeatRunner(scene, scene_id, start_time)
    builder(scene, runner)
    runner.finish()
    return runner


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------
def title(text: str, size: int = TITLE_SIZE, color: str = INK) -> Text:
    return Text(text, font_size=size, color=color)


def label(text: str, size: int = LABEL_SIZE, color: str = INK) -> Text:
    return Text(text, font_size=size, color=color)


def small(text: str, size: int = SMALL_SIZE, color: str = INK_DIM) -> Text:
    return Text(text, font_size=size, color=color)


def eq(*tex: str, size: int = EQUATION_SIZE, color: str = INK, **kwargs) -> MathTex:
    return MathTex(*tex, font_size=size, color=color, **kwargs)


class DigitReadout(VGroup):
    """A live numeric readout built from glyphs that already exist.

    Manim's DecimalNumber rebuilds its submobjects on every ``set_value``.  With
    the LaTeX default that shells out to LaTeX per distinct value; with
    ``mob_class=Text`` the stored value updates but the rendered glyphs go
    stale.  So instead every slot here holds all ten digits stacked at one
    position, pre-built once, and ``set_value`` only toggles opacity.  Nothing
    is constructed or compiled while the animation runs.

    Attach the updater that drives this readout **to the readout itself**.
    Manim bakes every mobject that sits before the first moving mobject into a
    static cached image for the duration of a ``play``, so a readout mutated
    from some other mobject's updater silently renders its old value.
    """

    _CHARS = "0123456789"

    def __init__(self, value: float = 0.0, places: int = 2, int_digits: int = 1,
                 signed: bool = False, size: int = LABEL_SIZE,
                 color: str = CYAN, **kwargs):
        super().__init__(**kwargs)
        self.places = places
        self.int_digits = int_digits
        self.signed = signed
        self._slots: list[dict[str, Text]] = []

        probe = Text("0", font_size=size, color=color)
        slot_width = probe.width * 1.06
        cursor = 0.0

        baseline = probe.get_bottom()[1]
        middle = probe.get_center()[1]

        def add_slot(chars: str, width: float):
            nonlocal cursor
            glyphs: dict[str, Text] = {}
            for char in chars:
                glyph = Text(char, font_size=size, color=color)
                glyph.move_to(RIGHT * (cursor + width / 2))
                # Digits and the point sit on the baseline; a centred point
                # would render as a mid-dot.  The sign stays vertically centred.
                if char in "+-":
                    glyph.shift(UP * (middle - glyph.get_center()[1]))
                else:
                    glyph.shift(UP * (baseline - glyph.get_bottom()[1]))
                glyph.set_opacity(0.0)
                glyphs[char] = glyph
                self.add(glyph)
            self._slots.append(glyphs)
            cursor += width

        if signed:
            add_slot("+-", slot_width * 0.62)
        for _ in range(int_digits):
            add_slot(self._CHARS, slot_width)
        if places > 0:
            add_slot(".", slot_width * 0.45)
            for _ in range(places):
                add_slot(self._CHARS, slot_width)

        self.move_to(ORIGIN)
        self.set_value(value)

    def _text(self, value: float) -> str:
        limit = 10**self.int_digits - 10 ** (-self.places)
        value = float(np.clip(value, -limit, limit))
        body = f"{abs(value):0{self.int_digits + (self.places + 1 if self.places else 0)}.{self.places}f}"
        return (("-" if value < 0 else "+") if self.signed else "") + body

    def set_value(self, value: float):
        for glyphs, char in zip(self._slots, self._text(value)):
            for key, glyph in glyphs.items():
                glyph.set_opacity(1.0 if key == char else 0.0)
        self._value = float(value)
        return self

    def get_value(self) -> float:
        return self._value


def live_number(value: float = 0.0, places: int = 4, size: int = LABEL_SIZE,
                color: str = CYAN, int_digits: int = 1,
                signed: bool = False) -> DigitReadout:
    """A value readout that neither compiles LaTeX nor rebuilds glyphs."""
    return DigitReadout(value, places=places, int_digits=int_digits,
                        signed=signed, size=size, color=color)


def place_top(mobject, offset: float = 0.0):
    mobject.move_to([mobject.get_center()[0], SAFE_TOP - offset, 0])
    return mobject


def caption(text: str, size: int = SMALL_SIZE, color: str = INK_DIM) -> Text:
    """A short line that sits above the reserved subtitle band."""
    return small(text, size=size, color=color).move_to([0, SAFE_BOTTOM + 0.35, 0])


def swap_equation(scene: Scene, old, new, run_time: float = 0.8):
    """Transform one equation into another, matching symbols where possible."""
    if isinstance(old, MathTex) and isinstance(new, MathTex):
        scene.play(TransformMatchingTex(old, new), run_time=run_time)
    else:
        scene.play(Transform(old, new), run_time=run_time)
    return new


# ---------------------------------------------------------------------------
# Complex panels
# ---------------------------------------------------------------------------
class ComplexPanel:
    """A light, secondary coordinate frame that maps complex numbers to points.

    Scene 4 onward shows two of these side by side at the same visual scale,
    so a length on the left means the same as a length on the right.
    """

    def __init__(self, centre=ORIGIN, unit: float = 1.0, half_width: float = 3.0,
                 half_height: float = 2.4, axis_color: str = INK_DIM,
                 x_label: str | None = None, y_label: str | None = None,
                 name: str | None = None, y_span: tuple[float, float] | None = None,
                 name_below: float | None = None, y_label_dir=RIGHT):
        """``y_span`` gives the vertical axis an asymmetric reach, in complex
        units, for a panel whose interesting values run far in one direction --
        scene 5's accumulation runs up to 2*pi and nowhere below."""
        self.centre = np.array(centre, dtype=float)
        self.unit = float(unit)
        self.half_width = half_width
        self.half_height = half_height

        low, high = ((-half_height / self.unit, half_height / self.unit)
                     if y_span is None else y_span)
        horizontal = Line(self.centre + LEFT * half_width,
                          self.centre + RIGHT * half_width,
                          stroke_width=1.4, color=axis_color, stroke_opacity=0.55)
        vertical = Line(self.centre + UP * (low * self.unit),
                        self.centre + UP * (high * self.unit),
                        stroke_width=1.4, color=axis_color, stroke_opacity=0.55)
        self.axes = VGroup(horizontal, vertical)
        self.decorations = VGroup()

        if x_label:
            tag = small(x_label, color=axis_color)
            tag.next_to(horizontal.get_end(), DOWN, buff=0.14).shift(LEFT * 0.1)
            self.decorations.add(tag)
        if y_label:
            tag = small(y_label, color=axis_color)
            tag.next_to(vertical.get_end(), y_label_dir, buff=0.14)
            self.decorations.add(tag)
        if name:
            tag = small(name, color=axis_color)
            drop = half_height + 0.42 if name_below is None else name_below
            tag.move_to(self.centre + DOWN * drop)
            self.decorations.add(tag)
            self.name_tag = tag

        self.group = VGroup(self.axes, self.decorations)

    def c2p(self, z) -> np.ndarray:
        """Complex number -> scene point."""
        z = complex(z)
        return self.centre + np.array([z.real * self.unit, z.imag * self.unit, 0.0])

    def c2p_many(self, values) -> np.ndarray:
        values = np.asarray(values, dtype=complex)
        points = np.zeros((values.size, 3))
        points[:, 0] = self.centre[0] + values.real * self.unit
        points[:, 1] = self.centre[1] + values.imag * self.unit
        points[:, 2] = self.centre[2]
        return points

    def tick(self, z, text: str, color: str = INK_DIM, direction=RIGHT):
        """A labelled tick that makes an endpoint reading truthful."""
        point = self.c2p(z)
        mark = Line(point + LEFT * 0.09, point + RIGHT * 0.09,
                    stroke_width=2.2, color=color)
        tag = small(text, color=color).next_to(point, direction, buff=0.16)
        return VGroup(mark, tag)


# ---------------------------------------------------------------------------
# The contribution chain
# ---------------------------------------------------------------------------
class ContributionChain(VMobject):
    """The gold accumulation path, drawn from precomputed integral samples.

    The chain is never a set of visually guessed arrows: it is the running
    contour integral, so its endpoint is a real reading.
    """

    def __init__(self, panel: ComplexPanel, samples, color: str = GOLD,
                 stroke_width: float = 3.4, **kwargs):
        super().__init__(color=color, stroke_width=stroke_width, **kwargs)
        self.panel = panel
        self.samples = np.asarray(samples, dtype=complex)
        self.points_cache = panel.c2p_many(self.samples)
        self.set_points_as_corners(self.points_cache[:2])

    def show_fraction(self, fraction: float):
        """Reveal the chain up to a fraction of the traversal."""
        count = max(2, int(np.clip(fraction, 0.0, 1.0) * (len(self.points_cache) - 1)) + 1)
        self.set_points_as_corners(self.points_cache[:count])
        return self

    def endpoint(self) -> np.ndarray:
        return self.points_cache[-1]

    def value_at(self, fraction: float) -> complex:
        index = int(np.clip(fraction, 0.0, 1.0) * (len(self.samples) - 1))
        return complex(self.samples[index])


def grow_chain(scene: Scene, chain: ContributionChain, run_time: float,
               tip: Dot | None = None, extra=()):
    """Reveal a chain incrementally, dragging an optional tip marker with it."""
    tracker = ValueTracker(0.0)

    def update(mobject):
        fraction = tracker.get_value()
        mobject.show_fraction(fraction)
        if tip is not None:
            tip.move_to(mobject.get_points()[-1])
        for callback in extra:
            callback(fraction)

    chain.add_updater(update)
    scene.play(tracker.animate.set_value(1.0), run_time=run_time, rate_func=lambda t: t)
    chain.remove_updater(update)
    chain.show_fraction(1.0)
    if tip is not None:
        tip.move_to(chain.endpoint())


# ---------------------------------------------------------------------------
# Energy bars and the work meter
# ---------------------------------------------------------------------------
class EnergyBars(VGroup):
    """Potential and kinetic bars inside one fixed total-energy outline.

    The outline never changes height, which is the whole point: the two bars
    trade, the total does not move.
    """

    def __init__(self, total: float, height: float = 2.4, width: float = 0.34,
                 gap: float = 0.26, **kwargs):
        super().__init__(**kwargs)
        self.total = float(total)
        self.bar_height = height
        self.bar_width = width

        self.pe_bar = Rectangle(width=width, height=1e-3, fill_color=VIOLET,
                                fill_opacity=0.9, stroke_width=0)
        self.ke_bar = Rectangle(width=width, height=1e-3, fill_color=TEAL,
                                fill_opacity=0.9, stroke_width=0)
        self.pe_slot = Rectangle(width=width, height=height, stroke_width=1.2,
                                 stroke_color=INK_DIM, stroke_opacity=0.5)
        self.ke_slot = self.pe_slot.copy()
        self.ke_slot.next_to(self.pe_slot, RIGHT, buff=gap)

        self.total_outline = Rectangle(
            width=width * 2 + gap + 0.22, height=height + 0.16,
            stroke_width=1.6, stroke_color=INK, stroke_opacity=0.65)
        self.total_outline.move_to(VGroup(self.pe_slot, self.ke_slot).get_center())

        self.pe_label = small("PE", color=VIOLET).next_to(self.pe_slot, DOWN, buff=0.12)
        self.ke_label = small("KE", color=TEAL).next_to(self.ke_slot, DOWN, buff=0.12)
        self.total_label = small("Total energy", color=INK).next_to(
            self.total_outline, UP, buff=0.14)

        self.add(self.total_outline, self.pe_slot, self.ke_slot,
                 self.pe_bar, self.ke_bar,
                 self.pe_label, self.ke_label, self.total_label)
        self.set_state(self.total * 0.5, self.total * 0.5)

    def set_state(self, potential: float, kinetic: float):
        """Drive both bars from one physical state -- never independently."""
        for bar, slot, amount in ((self.pe_bar, self.pe_slot, potential),
                                  (self.ke_bar, self.ke_slot, kinetic)):
            fraction = float(np.clip(amount / self.total, 1e-4, 1.0))
            bar.stretch_to_fit_height(self.bar_height * fraction)
            bar.move_to(slot.get_bottom() + UP * (self.bar_height * fraction / 2))
        return self


class WorkMeter(VGroup):
    """A signed meter for the work done by gravity -- not an energy display."""

    def __init__(self, span: float, width: float = 2.6, name: str = "Work by gravity",
                 **kwargs):
        super().__init__(**kwargs)
        self.span = float(span)
        self.width = width
        self.axis = Line(LEFT * width / 2, RIGHT * width / 2,
                         stroke_width=1.6, color=INK_DIM)
        self.zero_mark = Line(DOWN * 0.12, UP * 0.12, stroke_width=1.8, color=INK_DIM)
        self.bar = Line(ORIGIN, ORIGIN, stroke_width=7, color=GOLD)
        self.name = small(name, color=INK).next_to(self.axis, UP, buff=0.16)
        self.readout = live_number(0.0, places=2, size=SMALL_SIZE, color=GOLD)
        self.readout.next_to(self.axis, DOWN, buff=0.16)
        self.add(self.axis, self.zero_mark, self.bar, self.name, self.readout)
        self.set_work(0.0)

    def set_work(self, work: float):
        fraction = float(np.clip(work / self.span, -1.0, 1.0))
        end = self.axis.get_center() + RIGHT * (fraction * self.width / 2)
        if abs(fraction) < 1e-4:
            end = self.axis.get_center() + RIGHT * 1e-3
        self.bar.put_start_and_end_on(self.axis.get_center(), end)
        self.bar.set_color(GOLD if work >= 0 else CORAL)
        self.readout.set_value(work)
        return self


# ---------------------------------------------------------------------------
# Singularities and residues
# ---------------------------------------------------------------------------
def pole_marker(panel: ComplexPanel, z, radius: float = 0.075,
                color: str = CORAL) -> Dot:
    """A pole dot with a guaranteed minimum size, so it never vanishes."""
    return Dot(panel.c2p(z), radius=radius, color=color)


def residue_label(panel: ComplexPanel, z, text: str, color: str = GOLD,
                  direction=UP, buff: float = 0.2, size: int = SMALL_SIZE):
    return eq(text, size=size, color=color).next_to(panel.c2p(z), direction, buff=buff)


def weight_glyph(panel: ComplexPanel, z, residue: float, unit_radius: float = 0.26,
                 color: str = GOLD) -> Circle:
    """A disc whose AREA is proportional to the residue, not its height."""
    radius = unit_radius * np.sqrt(abs(residue))
    return Circle(radius=max(radius, 0.05), color=color, fill_color=color,
                  fill_opacity=0.28, stroke_width=1.4).move_to(panel.c2p(z))


def dashed_arrow(start, end, color: str = INK, stroke_width: float = 3.0,
                 dash_length: float = 0.09, tip_length: float = 0.16):
    """A dashed arrow -- the 'along' part of a split flow arrow."""
    line = DashedLine(start, end, dash_length=dash_length, color=color,
                      stroke_width=stroke_width)
    line.add_tip(tip_length=tip_length)
    return line


def solid_arrow(start, end, color: str = SLATE, stroke_width: float = 3.0,
                tip_length: float = 0.16):
    """A solid arrow -- the 'across' part of a split flow arrow."""
    return Arrow(start, end, color=color, stroke_width=stroke_width,
                 buff=0, tip_length=tip_length,
                 max_tip_length_to_length_ratio=0.45,
                 max_stroke_width_to_length_ratio=12)


def ghost(mobject, opacity: float = 0.3, color: str = GHOST):
    """Dim a superseded copy so it reads as a memory, not a live object."""
    return mobject.copy().set_stroke(color=color, opacity=opacity).set_fill(opacity=0)
