#!/usr/bin/env python3
"""Acceptance checks for the Basel film -- run this BEFORE rendering.

Every numeric claim the animation makes on screen is checked here against its
analytic value.  Nothing in the scenes snaps an endpoint into place; if a chain
does not close, this script is where that shows up.

    python3 tools/verify_math.py
"""

from __future__ import annotations

import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from basel.mathcore import (  # noqa: E402
    advect_particles, along_across_fields, basel_residue, basel_residue_sum,
    boundary_bound, circle_path, cot_pi, decompose_step, f_basel, f_identity,
    f_inverse, f_inverse_sq, flow_field, running_integral,
    running_integral_exact_identity, running_integral_exact_inverse,
    square_path,
)

FAILURES: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def close(a, b, tol=1e-6) -> bool:
    return bool(np.all(np.abs(np.asarray(a) - np.asarray(b)) < tol))


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


# ---------------------------------------------------------------------------
section("Scene 2-3: coaster energy and path independence")
# ---------------------------------------------------------------------------
from basel.coaster import Coaster  # noqa: E402

coaster = Coaster()
s = np.linspace(0.0, coaster.length, 4000)
heights = coaster.height_at(s)
speeds = coaster.speed_at(s)
energy = 0.5 * speeds**2 + coaster.g * heights
check("mechanical energy is constant around the ride",
      close(energy, energy[0], 1e-9),
      f"spread {energy.max() - energy.min():.2e}")
check("the car keeps real speed everywhere (loop is cleared)",
      bool(np.all(speeds > 0.2)), f"min speed {speeds.min():.3f}")
check("speed at A returns to its starting value",
      close(coaster.speed_at(0.0), coaster.speed_at(coaster.length), 1e-9))
pe = coaster.potential_at(s)
ke = coaster.kinetic_at(s)
check("the two bars always fill exactly one fixed total-energy outline",
      close(pe + ke, coaster.bar_total, 1e-9),
      f"PE+KE spread {(pe + ke).max() - (pe + ke).min():.2e}")
check("neither bar ever goes negative or overflows its slot",
      bool(np.all(pe >= -1e-12) and np.all(ke >= 0) and np.all(pe <= coaster.bar_total + 1e-12)
           and np.all(ke <= coaster.bar_total + 1e-12)))
check("gravity's work around the closed ride is zero",
      close(coaster.work_at(coaster.length), 0.0, 1e-9),
      f"{coaster.work_at(coaster.length):.2e}")

from basel.coaster import TwoRoutes  # noqa: E402

routes = TwoRoutes()
w_solid = routes.work("solid")
w_dashed = routes.work("dashed")
check("both routes from A to B do the same work",
      close(w_solid, w_dashed, 1e-9), f"{w_solid:.6f} vs {w_dashed:.6f}")
check("that work equals U(A) - U(B)",
      close(w_solid, routes.potential_drop(), 1e-9))
check("the two routes take genuinely different times",
      abs(routes.travel_time("solid") - routes.travel_time("dashed")) > 0.05,
      f"{routes.travel_time('solid'):.3f}s vs {routes.travel_time('dashed'):.3f}s")

# ---------------------------------------------------------------------------
section("Scene 4: along + i*across is exactly f dz")
# ---------------------------------------------------------------------------
path = circle_path(1.6, samples=4001)
rng = np.random.default_rng(7)
worst_identity = 0.0
for index in rng.integers(0, len(path) - 1, 400):
    z = path[index]
    dz = path[index + 1] - path[index]
    along, across, contribution = decompose_step(f_identity, z, dz)
    worst_identity = max(worst_identity,
                         abs((along + 1j * across) * abs(dz) - contribution))
check("f dz == (along + i*across)*|dz| at every sampled step",
      worst_identity < 1e-12, f"worst error {worst_identity:.2e}")

# along really is the fluid dotted with the direction of travel
z = path[500]
dz = path[501] - path[500]
P = complex(flow_field(f_identity, z))
tangent = dz / abs(dz)
along, across, _c = decompose_step(f_identity, z, dz)
dot_along = P.real * tangent.real + P.imag * tangent.imag
dot_across = P.real * tangent.imag - P.imag * tangent.real
check("along == P . (direction of travel)", close(along, dot_along, 1e-12))
check("across == P . (direction right of travel)", close(across, dot_across, 1e-12))

# Compare at the chord midpoint: the finite-difference tangent belongs there,
# not at the sample point, so this is exact rather than off by half a step.
midpoint = 0.5 * (path[500] + path[501])
outward = midpoint / abs(midpoint)
check("right of travel is outward on a counterclockwise loop",
      close(complex(-1j * tangent), outward, 1e-9))

integral = running_integral(f_identity, path)
check("f(z)=z: circulation of the saddle flow is zero",
      close(integral[-1].real, 0.0, 1e-9), f"{integral[-1].real:.2e}")
check("f(z)=z: flux of the saddle flow is zero",
      close(integral[-1].imag, 0.0, 1e-9), f"{integral[-1].imag:.2e}")
check("f(z)=z: sampled chain matches the primitive z^2/2 everywhere",
      close(integral, running_integral_exact_identity(path), 1e-4),
      f"max drift {np.abs(integral - running_integral_exact_identity(path)).max():.2e}")

# ---------------------------------------------------------------------------
section("Scene 5: the sprinkler and 2 pi i")
# ---------------------------------------------------------------------------
for radius in (0.6, 1.0, 1.4, 2.2):
    loop = circle_path(radius, samples=6001)
    total = running_integral(f_inverse, loop)[-1]
    check(f"1/z at r={radius}: circulation 0, flux 2*pi",
          close(total.real, 0.0, 1e-8) and close(total.imag, 2 * np.pi, 1e-5),
          f"{total.real:+.2e} + i*{total.imag:.6f}")

loop = circle_path(1.0, samples=6001)
check("1/z: exact log primitive also lands on 2*pi*i",
      close(running_integral_exact_inverse(loop)[-1], 2j * np.pi, 1e-12))

# the sprinkler: outward speed 1/r, so flux = (1/r)*2*pi*r = 2*pi
for radius in (0.5, 1.0, 3.0):
    loop = circle_path(radius, samples=4001)
    P = flow_field(f_inverse, loop)
    outward_unit = loop / np.abs(loop)
    outward_speed = P.real * outward_unit.real + P.imag * outward_unit.imag
    check(f"1/z fluid at r={radius} is purely outward at speed 1/r",
          close(outward_speed, 1.0 / radius, 1e-9))
    along, across = along_across_fields(f_inverse, loop)
    check(f"1/z at r={radius}: nothing pushes along the circle",
          close(along, 0.0, 1e-9), f"max |along| {np.abs(along).max():.2e}")

# ---------------------------------------------------------------------------
section("Scene 6: blows up, but does not leak")
# ---------------------------------------------------------------------------
loop = circle_path(1.0, samples=6001)
total = running_integral(f_inverse_sq, loop)[-1]
check("1/z^2: circulation is zero", close(total.real, 0.0, 1e-8))
check("1/z^2: flux is zero", close(total.imag, 0.0, 1e-8))

t = np.angle(loop)
P = flow_field(f_inverse_sq, loop)
outward_unit = loop / np.abs(loop)
outward_speed = P.real * outward_unit.real + P.imag * outward_unit.imag
check("1/z^2: outward component on the unit circle is exactly cos(t)",
      close(outward_speed, np.cos(t), 1e-9),
      "fluid leaves on the right and returns on the left")

# ---------------------------------------------------------------------------
section("Scene 7-8: residues of pi*cot(pi z)/z^2")
# ---------------------------------------------------------------------------
for n in (-4, -3, -2, -1, 1, 2, 3, 4):
    small = circle_path(0.25, centre=complex(n), samples=6001)
    total = running_integral(f_basel, small)[-1]
    residue = total / (2j * np.pi)
    check(f"residue at n={n:+d} is 1/n^2 = {1/n**2:.6f}",
          close(residue, basel_residue(n), 1e-6),
          f"got {residue.real:+.6f}{residue.imag:+.2e}i")

small = circle_path(0.25, centre=0.0, samples=8001)
residue_zero = running_integral(f_basel, small)[-1] / (2j * np.pi)
check("residue at the origin is -pi^2/3",
      close(residue_zero, -np.pi**2 / 3, 1e-6),
      f"got {residue_zero.real:+.6f}, want {-np.pi**2/3:+.6f}")
check("the origin's residue is real, so it is a pure drain",
      close(residue_zero.imag, 0.0, 1e-8))

# the 1/z^3 term carries no residue -- that is why only -pi^2/3 survives
local = circle_path(0.3, samples=4001)
cube = running_integral(lambda w: 1.0 / w**3, local)[-1]
check("the reciprocal-cube term integrates to zero around the loop",
      close(cube, 0.0, 1e-8))

# cross-check the expansion pi*cot(pi z)/z^2 = 1/z^3 - pi^2/(3z) + O(z)
probe = np.array([0.02, 0.03, -0.025, 0.02j, -0.03j])
remainder = f_basel(probe) - (1 / probe**3 - np.pi**2 / (3 * probe))
# The next term of pi*cot(pi z) is -pi^4 z^3/45, so after dividing by z^2 the
# remainder must behave like (pi^4/45)*|z| -- genuinely O(z), with a known slope.
ratio = np.abs(remainder) / np.abs(probe)
check("local expansion 1/z^3 - pi^2/(3z) + O(z) is correct near zero",
      close(ratio, np.pi**4 / 45, 2e-3),
      f"remainder/|z| = {ratio.mean():.6f}, pi^4/45 = {np.pi**4/45:.6f}")

# ---------------------------------------------------------------------------
section("Scene 9: the squares C_N")
# ---------------------------------------------------------------------------
for N in (2, 3, 5, 10):
    R = N + 0.5
    contour = square_path(R, samples_per_side=4000)
    total = running_integral(f_basel, contour)[-1]
    want = 2j * np.pi * basel_residue_sum(N)
    check(f"C_{N} (R={R}): circulation is exactly zero",
          close(total.real, 0.0, 1e-6), f"{total.real:+.2e}")
    check(f"C_{N} (R={R}): flux matches 2*pi*(sum of residues)",
          close(total.imag, want.imag, 2e-3),
          f"{total.imag:+.6f} vs {want.imag:+.6f}")
    check(f"C_{N}: |integral| respects the 16*pi/R bound",
          abs(total) <= boundary_bound(R) + 1e-9,
          f"|I|={abs(total):.4f} <= {boundary_bound(R):.4f}")

# the bound's own ingredient: |cot(pi z)| <= 2 on these squares
worst_cot = 0.0
for N in range(0, 12):
    contour = square_path(N + 0.5, samples_per_side=2000)
    worst_cot = max(worst_cot, float(np.abs(cot_pi(contour)).max()))
check("|cot(pi z)| <= 2 on every square C_N, N >= 0",
      worst_cot <= 2.0, f"observed sup {worst_cot:.4f}")
check("the bound 16*pi/R is monotonically decreasing",
      all(boundary_bound(r) > boundary_bound(r + 1) for r in range(2, 40)))

# ---------------------------------------------------------------------------
section("Scene 10: the sum resolves")
# ---------------------------------------------------------------------------
# 0 = -pi^2/3 + 2*S  =>  S = pi^2/6
tail = basel_residue_sum(200000)
implied = (np.pi**2 / 3) / 2
check("0 = residue(0) + 2*S forces S = pi^2/6",
      close(implied, np.pi**2 / 6, 1e-12), f"pi^2/6 = {np.pi**2/6:.6f}")
check("the partial sums are converging to it",
      abs(tail) < 1e-4, f"residue sum at N=200000 is {tail:.2e}")
check("the opening target tick 1.644934 is pi^2/6 rounded",
      close(round(np.pi**2 / 6, 6), 1.644934, 1e-12))

# ---------------------------------------------------------------------------
section("Flow layer: particles follow conj(f), never f")
# ---------------------------------------------------------------------------
seeds = np.array([0.8 + 0.3j, -1.2 + 0.7j, 0.4 - 1.1j, 2.0 + 0.1j])
for name, func in (("z", f_identity), ("1/z", f_inverse), ("1/z^2", f_inverse_sq)):
    track = advect_particles(func, seeds, steps=40, dt=0.01, poles=(0,),
                             pole_radius=0.25, bounds=4.0)
    step = track[1] - track[0]
    expected = np.conj(func(track[0]))
    aligned = np.all((step.real * expected.real + step.imag * expected.imag) > 0)
    check(f"particles for f={name} move along conj(f), not f", bool(aligned))

track = advect_particles(f_inverse, seeds, steps=600, dt=0.01, poles=(0,),
                         pole_radius=0.25, bounds=4.0)
check("no particle is ever advected through a pole",
      bool(np.all(np.abs(track) >= 0.24)),
      f"closest approach {np.abs(track).min():.3f}")

radial = advect_particles(f_inverse, np.array([1.0 + 0j]), steps=50, dt=0.01,
                          poles=(0,), pole_radius=0.25, bounds=4.0)
check("the sprinkler pushes particles outward",
      bool(np.abs(radial[-1, 0]) > np.abs(radial[0, 0])),
      f"|z| {abs(radial[0,0]):.3f} -> {abs(radial[-1,0]):.3f}")

# ---------------------------------------------------------------------------
section("Timing map")
# ---------------------------------------------------------------------------
from basel.config import SCENE_ORDER, beat_times, scene_duration, total_duration  # noqa: E402

check("the ten scene durations total exactly 120 s",
      close(total_duration(), 120.0, 1e-9), f"{total_duration():.3f}s")
for scene_id in SCENE_ORDER:
    beats = beat_times(scene_id)
    spans_match = close(beats[-1][2], scene_duration(scene_id), 1e-9)
    contiguous = all(close(beats[i][2], beats[i + 1][1], 1e-9)
                     for i in range(len(beats) - 1))
    check(f"scene {scene_id}: beats tile its {scene_duration(scene_id):.0f}s exactly",
          spans_match and contiguous)

# ---------------------------------------------------------------------------
print("\n" + "=" * 62)
if FAILURES:
    print(f"{len(FAILURES)} of {CHECKS} checks FAILED:")
    for name in FAILURES:
        print(f"  - {name}")
    sys.exit(1)
print(f"All {CHECKS} checks passed.")
