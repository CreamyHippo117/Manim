"""Numerics for the Basel film.

Two ideas carry the whole flux layer and both live here:

* The fluid drawn on screen is always ``P = conj(f)``, never ``f``.
* With that fluid, ``f(z) dz`` splits as ``(along + i*across)*|dz|`` where
  ``along`` is the component of ``P`` along the direction of travel and
  ``across`` is the component to the *right* of travel -- outward on a
  counterclockwise loop.

The algebra: write ``dz = T|dz|`` with ``T`` the unit tangent.  Then

    f(z) dz = conj(P) T |dz|

and with ``P = p1 + i p2``, ``T = t1 + i t2``,

    conj(P) T = (p1 t1 + p2 t2) + i (p1 t2 - p2 t1)
              = (P . T)         + i (P . n_right)

since rotating ``T`` by -90 degrees gives ``n_right = (t2, -t1)``.  So the real
part of a contour integral is the circulation of ``P`` and the imaginary part
is its flux out of the curve.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# The functions the film uses
# --------------------------------------------------------------------------


def f_identity(z):
    """f(z) = z.  Its fluid conj(z) = x - iy is the saddle flow of scene 4."""
    return z


def f_inverse(z):
    """f(z) = 1/z.  Its fluid conj(1/z) = z/|z|^2 is the sprinkler of scene 5."""
    return 1.0 / z


def f_inverse_sq(z):
    """f(z) = 1/z^2.  Blows up, but does not leak: the dipole of scene 6."""
    return 1.0 / z**2


def cot_pi(z):
    """cot(pi z), evaluated stably for any imaginary part.

    Using cos/sin directly overflows once |Im z| is large.  The exponential
    form is stable for Im z >= 0, and the reflection cot(pi conj(z)) =
    conj(cot(pi z)) covers the lower half plane.
    """
    z = np.asarray(z, dtype=complex)
    upper = np.where(z.imag >= 0, z, np.conj(z))
    e = np.exp(2j * np.pi * upper)
    result = 1j * (e + 1.0) / (e - 1.0)
    result = np.where(z.imag >= 0, result, np.conj(result))
    return result if result.shape else complex(result)


def f_basel(z):
    """f(z) = pi*cot(pi z) / z^2 -- the function the whole proof is built on.

    Residue 1/n^2 at every nonzero integer n, and -pi^2/3 at the origin.
    """
    return np.pi * cot_pi(z) / np.asarray(z, dtype=complex) ** 2


# --------------------------------------------------------------------------
# Contours
# --------------------------------------------------------------------------


def circle_path(radius=1.0, centre=0.0 + 0j, samples=2001, turns=1.0, start=0.0):
    """Counterclockwise circular contour, sampled uniformly in angle."""
    t = np.linspace(start, start + turns * 2 * np.pi, samples)
    return centre + radius * np.exp(1j * t)


def square_path(half_width, samples_per_side=600):
    """Counterclockwise square contour with corners at (+-R, +-R).

    Scene 9 uses R = N + 1/2 so the contour runs exactly halfway between two
    adjacent real-axis poles.
    """
    R = float(half_width)
    s = np.linspace(-R, R, samples_per_side, endpoint=False)
    bottom = s + (-R) * 1j                     # left to right along y = -R
    right = R + s * 1j                         # bottom to top along x = +R
    top = (-s) + R * 1j                        # right to left along y = +R
    left = (-R) + (-s) * 1j                    # top to bottom along x = -R
    loop = np.concatenate([bottom, right, top, left])
    return np.append(loop, loop[0])            # close it


# --------------------------------------------------------------------------
# Accumulation
# --------------------------------------------------------------------------


def running_integral(f, path):
    """Cumulative trapezoidal contour integral along ``path``.

    Returns an array the same length as ``path`` whose k-th entry is the
    integral from path[0] to path[k].  This is what the gold chain draws, so
    the chain is never a visually guessed set of arrows.
    """
    path = np.asarray(path, dtype=complex)
    values = f(path)
    dz = np.diff(path)
    midpoint = 0.5 * (values[:-1] + values[1:])
    return np.concatenate([[0.0 + 0j], np.cumsum(midpoint * dz)])


def running_integral_exact_identity(path):
    """Exact running integral of f(z) = z, from the primitive z^2/2."""
    path = np.asarray(path, dtype=complex)
    return (path**2 - path[0] ** 2) / 2.0


def running_integral_exact_inverse(path, centre=0.0 + 0j):
    """Exact running integral of 1/z along a path that never crosses the cut.

    Uses the continuous (unwrapped) argument so one counterclockwise turn ends
    at exactly 2*pi*i instead of jumping at the branch cut.
    """
    w = np.asarray(path, dtype=complex) - centre
    angle = np.unwrap(np.angle(w))
    return (np.log(np.abs(w)) + 1j * angle) - (np.log(abs(w[0])) + 1j * angle[0])


def decompose_step(f, z, dz):
    """Split one flow arrow at one path point into its along and across parts.

    Returns ``(along, across, contribution)`` where ``contribution`` is the
    complex number ``f(z) dz`` and

        contribution == (along + 1j*across) * |dz|

    ``along`` is P dotted with the direction of travel; ``across`` is P dotted
    with the direction to the right of travel.
    """
    z = complex(z)
    dz = complex(dz)
    length = abs(dz)
    tangent = dz / length
    value = complex(f(z))          # note: conj(P) == f, so this is the product
    product = value * tangent
    return product.real, product.imag, value * dz


def flow_field(f, z):
    """The fluid: P = conj(f).  Never f itself."""
    return np.conj(f(np.asarray(z, dtype=complex)))


def along_across_fields(f, path):
    """Per-sample along and across components of the fluid on a whole path.

    A closed path gets a periodic central difference, so the tangent is exact
    at the seam too.  With a plain one-sided difference the first and last
    samples carry a first-order error, which is precisely where a "circulation
    is zero" reading would otherwise pick up spurious drift.
    """
    path = np.asarray(path, dtype=complex)
    closed = abs(path[-1] - path[0]) < 1e-12
    if closed:
        interior = path[:-1]
        dz = (np.roll(interior, -1) - np.roll(interior, 1)) / 2.0
        dz = np.append(dz, dz[0])
    else:
        dz = np.gradient(path)
    tangent = dz / np.abs(dz)
    product = f(path) * tangent
    return product.real, product.imag


# --------------------------------------------------------------------------
# Residues
# --------------------------------------------------------------------------


def basel_residue(n: int) -> float:
    """Residue of pi*cot(pi z)/z^2 at the integer n."""
    if n == 0:
        return -np.pi**2 / 3.0
    return 1.0 / float(n) ** 2


def basel_residue_sum(N: int) -> float:
    """Sum of residues inside the square C_N: the origin plus the paired ones."""
    return basel_residue(0) + 2.0 * sum(1.0 / k**2 for k in range(1, N + 1))


def boundary_bound(R: float) -> float:
    """The loose bound 16*pi/R on |integral over C_N|.

    On these squares |cot(pi z)| <= 2, the perimeter is 8R and |z| >= R, so
    |integral| <= 8R * (pi * 2) / R^2 = 16 pi / R.  A convenient loose bound,
    not an equality.
    """
    return 16.0 * np.pi / float(R)


# --------------------------------------------------------------------------
# Particle advection for the flow layer
# --------------------------------------------------------------------------


def advect_particles(f, seeds, steps, dt, poles=(), pole_radius=0.18,
                     bounds=6.0, speed_cap=2.5, seed=0):
    """Precompute particle trajectories by integrating the fluid P = conj(f).

    Particles move by the field, not by decorative drift.  A particle that
    comes within ``pole_radius`` of a pole -- or leaves ``bounds`` -- is
    respawned at a fresh random seed point, so nothing is ever advected
    through a singularity.

    Returns an array of shape (steps, len(seeds)) of complex positions.
    """
    rng = np.random.default_rng(seed)
    poles = np.asarray(poles, dtype=complex)
    position = np.asarray(seeds, dtype=complex).copy()
    track = np.empty((steps, position.size), dtype=complex)

    def respawn(count):
        return (rng.uniform(-bounds, bounds, count)
                + 1j * rng.uniform(-bounds, bounds, count))

    for step in range(steps):
        velocity = np.conj(f(position))
        magnitude = np.abs(velocity)
        # Cap speed so a near-pole particle cannot jump the frame in one step.
        too_fast = magnitude > speed_cap
        velocity[too_fast] = velocity[too_fast] / magnitude[too_fast] * speed_cap
        position = position + velocity * dt

        bad = (np.abs(position.real) > bounds) | (np.abs(position.imag) > bounds)
        if poles.size:
            near = np.min(np.abs(position[:, None] - poles[None, :]), axis=1)
            bad |= near < pole_radius
        if bad.any():
            position[bad] = respawn(int(bad.sum()))
        track[step] = position

    return track
