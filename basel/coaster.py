"""Track geometry and constant-energy motion for scenes 2 and 3.

Normalised units throughout: unit mass, g = 1, so the potential is just the
height and the total mechanical energy is ``0.5*v^2 + y``.

The car is *attached to the track*, so it stays on the rail through the loop;
we never claim an unrestrained car would.  Speed is computed from constant
mechanical energy and height, and the car advances along arc length, which is
what makes it visibly faster at the bottom.
"""

from __future__ import annotations

import numpy as np


def _smoothstep(t):
    """Smooth 0 -> 1 ramp with zero derivative at both ends."""
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


class Coaster:
    """A closed circuit: a peak at A, a descent, a vertical loop, a valley.

    The loop is inserted by adding ``r*(sin p, 1 - cos p)`` to a base oval,
    where ``p`` sweeps 0 -> 2*pi across a window of the parameter.  Because the
    offset and its derivative both vanish at ``p = 0`` and ``p = 2*pi``, the
    loop welds onto the base track with no kink and the circuit stays closed.
    """

    def __init__(self, width=3.4, height=1.6, centre_y=-0.3, loop_radius=0.75,
                 loop_window=(0.520, 0.556), g=1.0, speed_at_peak=1.15,
                 samples=6000):
        self.width = width
        self.height = height
        self.centre_y = centre_y
        self.loop_radius = loop_radius
        self.loop_window = loop_window
        self.g = g
        self.samples = samples

        u = np.linspace(0.0, 1.0, samples + 1)
        points = self._curve(u)
        self._u = u
        self._x = points.real
        self._y = points.imag

        # Arc length along the circuit.
        steps = np.abs(np.diff(points))
        self._s = np.concatenate([[0.0], np.cumsum(steps)])
        self.length = float(self._s[-1])

        # Constant mechanical energy, fixed by the speed we want at the peak A.
        self.peak_height = float(self._y.max())
        self.energy = 0.5 * speed_at_peak**2 + g * self.peak_height

        # Heights are measured from the lowest point of the track.  Without a
        # datum the potential would go negative in the valley and the kinetic
        # bar would overflow its slot -- the bars would stop reading as a trade.
        self.datum = float(self._y.min())
        self.bar_total = self.energy - g * self.datum

        # Physical time to complete the ride, for the playback acceleration.
        speeds = self.speed_at(self._s)
        midpoint = 0.5 * (1.0 / speeds[:-1] + 1.0 / speeds[1:])
        self._t = np.concatenate([[0.0], np.cumsum(midpoint * np.diff(self._s))])
        self.ride_time = float(self._t[-1])

    # -- geometry ----------------------------------------------------------
    def _curve(self, u):
        u = np.asarray(u, dtype=float)
        base = self.width * np.sin(2 * np.pi * u) + 1j * (
            self.centre_y + self.height * np.cos(2 * np.pi * u))
        start, end = self.loop_window
        ramp = _smoothstep((u - start) / (end - start))
        phase = 2 * np.pi * ramp
        offset = self.loop_radius * (np.sin(phase) + 1j * (1.0 - np.cos(phase)))
        return base + offset

    def point_at(self, s):
        """Position on the track at arc length s, as a complex number."""
        s = np.mod(np.asarray(s, dtype=float), self.length)
        return (np.interp(s, self._s, self._x)
                + 1j * np.interp(s, self._s, self._y))

    def height_at(self, s):
        s = np.mod(np.asarray(s, dtype=float), self.length)
        return np.interp(s, self._s, self._y)

    def tangent_at(self, s):
        """Unit tangent (direction of travel) at arc length s."""
        delta = self.length * 1e-4
        ahead = self.point_at(np.asarray(s) + delta)
        behind = self.point_at(np.asarray(s) - delta)
        step = ahead - behind
        return step / np.abs(step)

    # -- physics -----------------------------------------------------------
    def speed_at(self, s):
        """Speed from constant mechanical energy: v = sqrt(2(E - g*y))."""
        return np.sqrt(np.maximum(2.0 * (self.energy - self.g * self.height_at(s)),
                                  1e-9))

    def kinetic_at(self, s):
        return 0.5 * self.speed_at(s) ** 2

    def potential_at(self, s):
        """Potential above the lowest point of the track, so PE >= 0 always."""
        return self.g * (self.height_at(s) - self.datum)

    def work_at(self, s):
        """Work done by gravity from the start to arc length s: -(U(s) - U(0))."""
        return self.g * (self.height_at(0.0) - self.height_at(s))

    def arc_length_at_time(self, t):
        """Arc length reached after physical time t (t may be an array)."""
        return np.interp(np.asarray(t, dtype=float), self._t, self._s)

    def playback_rate(self, screen_seconds):
        """Physical seconds to play per screen second, so the ride just fits."""
        return self.ride_time / float(screen_seconds)


class TwoRoutes:
    """Two different routes from A to B, with B lower than A.

    Same endpoints, same starting speed, same energy -- so the same final speed
    and the same work by gravity, even though the routes have different lengths
    and different traversal times.
    """

    def __init__(self, a=(-4.2, 1.5), b=(4.2, -1.3), dip=2.4, rise=1.0,
                 g=1.0, start_speed=1.15, samples=3000):
        self.a = complex(*a)
        self.b = complex(*b)
        self.g = g
        self.samples = samples
        self._shape = {"solid": -abs(dip), "dashed": abs(rise)}

        peak = max(self.a.imag, self.b.imag,
                   max(self._profile(name, np.linspace(0, 1, 501)).imag.max()
                       for name in self._shape))
        self.energy = 0.5 * start_speed**2 + g * peak + 0.35
        self._cache = {name: self._build(name) for name in self._shape}

    def _profile(self, name, t):
        t = np.asarray(t, dtype=float)
        bulge = self._shape[name]
        x = self.a.real + (self.b.real - self.a.real) * t
        line = self.a.imag + (self.b.imag - self.a.imag) * t
        y = line + bulge * np.sin(np.pi * t)
        return x + 1j * y

    def _build(self, name):
        t = np.linspace(0.0, 1.0, self.samples + 1)
        points = self._profile(name, t)
        s = np.concatenate([[0.0], np.cumsum(np.abs(np.diff(points)))])
        speeds = np.sqrt(np.maximum(2.0 * (self.energy - self.g * points.imag), 1e-9))
        midpoint = 0.5 * (1.0 / speeds[:-1] + 1.0 / speeds[1:])
        times = np.concatenate([[0.0], np.cumsum(midpoint * np.diff(s))])
        return {"points": points, "s": s, "speed": speeds, "t": times}

    def points(self, name):
        return self._cache[name]["points"]

    def length(self, name):
        return float(self._cache[name]["s"][-1])

    def travel_time(self, name):
        return float(self._cache[name]["t"][-1])

    def point_at_time(self, name, t):
        data = self._cache[name]
        s = np.interp(t, data["t"], data["s"])
        return (np.interp(s, data["s"], data["points"].real)
                + 1j * np.interp(s, data["s"], data["points"].imag))

    def speed_at_time(self, name, t):
        data = self._cache[name]
        return np.interp(np.clip(t, 0, data["t"][-1]), data["t"], data["speed"])

    def work(self, name):
        """Work by gravity along the whole route: -(U(B) - U(A))."""
        points = self._cache[name]["points"]
        return float(self.g * (points.imag[0] - points.imag[-1]))

    def potential_drop(self):
        """U(A) - U(B): what the work has to equal, whichever route is taken."""
        return float(self.g * (self.a.imag - self.b.imag))
