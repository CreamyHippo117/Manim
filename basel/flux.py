"""The flux layer: the fluid, its particles, and the along/across split.

The one rule this module exists to enforce: **the fluid drawn on screen is
always P = conj(f), never f.**  ``FlowField.of`` takes ``f`` and conjugates it
for you; the only way to draw ``f`` itself is ``FlowField.raw``, which scene 5
uses for two seconds precisely to show how wrong it looks before the flip.
"""

from __future__ import annotations

import numpy as np
from manim import Arrow, Dot, VGroup
from manim import LEFT, RIGHT, UP, DOWN

from .config import (
    FLOW_ARROW_OPACITY, FLOW_PARTICLE_OPACITY, INK, SLATE, SLATE_DIM, SMALL_SIZE,
)
from .helpers import ComplexPanel, dashed_arrow, small, solid_arrow
from .mathcore import advect_particles


# ---------------------------------------------------------------------------
# Arrow grid
# ---------------------------------------------------------------------------
def _compress(magnitude, knee=1.0):
    """Squash a wild dynamic range into a drawable arrow length.

    Near a pole the true speed runs to infinity; drawn literally it would be a
    single arrow across the frame.  This keeps the *direction* honest and the
    length merely indicative.
    """
    return magnitude / (magnitude + knee)


class FlowField(VGroup):
    """A dim grid of arrows showing the fluid.  Always behind the contour."""

    def __init__(self, panel: ComplexPanel, field, x_range=(-2.4, 2.4),
                 y_range=(-2.0, 2.0), step: float = 0.55, arrow_scale: float = 0.42,
                 poles=(), pole_radius: float = 0.22, color: str = SLATE_DIM,
                 opacity: float = FLOW_ARROW_OPACITY, knee: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.panel = panel
        self.field = field
        poles = [complex(p) for p in poles]

        xs = np.arange(x_range[0], x_range[1] + 1e-9, step)
        ys = np.arange(y_range[0], y_range[1] + 1e-9, step)
        for x in xs:
            for y in ys:
                z = complex(x, y)
                if any(abs(z - p) < pole_radius for p in poles):
                    continue
                value = complex(field(np.array([z]))[0])
                magnitude = abs(value)
                if not np.isfinite(magnitude) or magnitude < 1e-9:
                    continue
                direction = value / magnitude
                length = arrow_scale * _compress(magnitude, knee)
                start = panel.c2p(z - direction * length / 2 / panel.unit)
                end = panel.c2p(z + direction * length / 2 / panel.unit)
                arrow = Arrow(start, end, buff=0, color=color,
                              stroke_width=2.0, tip_length=0.085,
                              max_tip_length_to_length_ratio=0.4,
                              max_stroke_width_to_length_ratio=10)
                arrow.set_opacity(opacity)
                self.add(arrow)

    @classmethod
    def of(cls, panel: ComplexPanel, f, **kwargs):
        """The fluid of ``f``: P = conj(f).  This is what viewers may see."""
        return cls(panel, lambda z: np.conj(f(z)), **kwargs)

    @classmethod
    def raw(cls, panel: ComplexPanel, f, **kwargs):
        """``f`` plotted directly as arrows -- reflected and confusing.

        Only scene 5 uses this, to motivate the conjugate before flipping it.
        """
        return cls(panel, f, **kwargs)


def flow_caption(text: str = "Flow = conj(f)", color: str = SLATE) -> "Text":
    """The label the fluid must carry the first time it appears, and on change."""
    return small(text, size=SMALL_SIZE, color=color)


# ---------------------------------------------------------------------------
# Particles
# ---------------------------------------------------------------------------
class ParticleLayer(VGroup):
    """Drifting dots that integrate the fluid, with trajectories precomputed.

    Nothing is advected through a pole: a particle that comes within
    ``pole_radius`` is respawned, which is handled in ``advect_particles``.
    The updater only moves existing dots -- it never builds new mobjects.
    """

    def __init__(self, panel: ComplexPanel, f, count: int = 70, steps: int = 900,
                 dt: float = 0.012, poles=(), pole_radius: float = 0.24,
                 bounds: float = 3.2, colour: str = SLATE, radius: float = 0.026,
                 opacity: float = FLOW_PARTICLE_OPACITY, speed_cap: float = 2.5,
                 seed: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.panel = panel
        rng = np.random.default_rng(seed)
        seeds = (rng.uniform(-bounds, bounds, count)
                 + 1j * rng.uniform(-bounds, bounds, count))
        self.track = advect_particles(f, seeds, steps=steps, dt=dt, poles=poles,
                                      pole_radius=pole_radius, bounds=bounds,
                                      speed_cap=speed_cap, seed=seed)
        self.steps = steps
        self.rate = 1.0 / dt          # advance one precomputed step per dt second
        self._phase = 0.0
        self.dots = VGroup(*[
            Dot(panel.c2p(self.track[0, i]), radius=radius, color=colour,
                fill_opacity=opacity, stroke_width=0)
            for i in range(count)
        ])
        self.add(self.dots)

    def _apply(self, index: int):
        positions = self.panel.c2p_many(self.track[index % self.steps])
        for dot, point in zip(self.dots, positions):
            dot.move_to(point)

    def start(self, speed: float = 1.0):
        """Begin drifting.  Works the same in a single scene or the overview."""
        def update(_mobject, dt):
            self._phase += dt * self.rate * speed
            self._apply(int(self._phase))

        self.add_updater(update)
        return self

    def stop(self):
        self.clear_updaters()
        return self


# ---------------------------------------------------------------------------
# Splitting one arrow at one point
# ---------------------------------------------------------------------------
class Decomposition(VGroup):
    """Split the flow arrow at one path point into its along and across parts.

    ``along`` is drawn as a dashed off-white arrow, ``across`` as a solid
    slate-blue one, each labelled -- so the two never rely on colour alone.
    Deliberately avoids the words divergence, curl and normal vector.
    """

    def __init__(self, panel: ComplexPanel, f, z, travel_direction,
                 arrow_scale: float = 1.0, show_labels: bool = True,
                 along_text: str = "along: push, like gravity's work",
                 across_text: str = "across: leak through the fence",
                 label_size: int = SMALL_SIZE, **kwargs):
        super().__init__(**kwargs)
        z = complex(z)
        tangent = complex(travel_direction)
        tangent /= abs(tangent)
        right_of_travel = -1j * tangent      # outward on a counterclockwise loop

        flow = complex(np.conj(f(np.array([z]))[0]))
        magnitude = abs(flow)
        draw = arrow_scale * _compress(magnitude, knee=1.0) / max(magnitude, 1e-9)

        base = panel.c2p(z)
        self.along_value = flow.real * tangent.real + flow.imag * tangent.imag
        self.across_value = flow.real * tangent.imag - flow.imag * tangent.real

        tip = panel.c2p(z + flow * draw)
        along_tip = panel.c2p(z + tangent * self.along_value * draw)
        across_tip = panel.c2p(z + right_of_travel * self.across_value * draw)

        self.flow_arrow = solid_arrow(base, tip, color=SLATE, stroke_width=4.0)
        self.along_arrow = dashed_arrow(base, along_tip, color=INK, stroke_width=3.4)
        self.across_arrow = solid_arrow(base, across_tip, color=SLATE, stroke_width=3.4)
        self.add(self.flow_arrow, self.along_arrow, self.across_arrow)

        if show_labels:
            self.along_label = small(along_text, size=label_size, color=INK)
            self.along_label.next_to(along_tip, UP, buff=0.14)
            self.across_label = small(across_text, size=label_size, color=SLATE)
            self.across_label.next_to(across_tip, RIGHT, buff=0.14)
            self.add(self.along_label, self.across_label)

    def contribution(self) -> complex:
        """(along + i*across) -- the shape of one gold link in the chain."""
        return complex(self.along_value, self.across_value)
