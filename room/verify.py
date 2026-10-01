#!/usr/bin/env python3
"""Check every number the script states against its analytic value."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from room import mathcore as mc

ok = True
def check(name, cond):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

check("one wall: 3.4 m / 340 m/s = 10 ms", np.isclose(3.4 / 340, 0.010))
check("arrivals ~1,000/s at 15 ms (100 m^3)", 900 < mc.arrival_rate(0.015) < 1300)
check("arrivals ~10,000/s at 45 ms", 9000 < mc.arrival_rate(0.045) < 11500)
check("comb notches 50/150/250 Hz for tau=10 ms",
      np.allclose(mc.comb_notch_hz(0.010), [50, 150, 250]))
a, tau = 0.6, 10
w = 2 * np.pi / 20  # omega*tau = pi/... arbitrary sweep
om = np.linspace(0, np.pi, 200)
check("|H|^2 closed form equals |1+a e^{-i w tau}|^2",
      np.allclose(mc.comb_mag2(om, tau, a), np.abs(mc.wall_H(om, tau, a)) ** 2))
check("comb depth 1-a and peak 1+a",
      np.isclose(np.sqrt(mc.comb_mag2(np.pi / tau, tau, a)), 1 - a)
      and np.isclose(np.sqrt(mc.comb_mag2(0, tau, a)), 1 + a))
check("T60 = ln(1000)/sigma ~ 6.9/sigma", np.isclose(mc.t60_from_sigma(1.0), 6.9, atol=0.01))
n = 16; h = np.array([1, 0, 0, .6, 0, .3])
x = np.random.default_rng(0).standard_normal(n)
H = mc.toeplitz_lower(h, n)
check("Toeplitz product equals np.convolve", np.allclose(H @ x, np.convolve(h, x)[:n]))
Hc = mc.circulant(h, 64)
w0 = 2 * np.pi * 5 / 64; e = np.exp(1j * w0 * np.arange(64))
lam = sum(h[m] * np.exp(-1j * w0 * m) for m in range(len(h)))
check("circulant: eigenvalue is H(omega)", np.allclose(Hc @ e, lam * e))
N, M = 40, 10; xs = np.random.default_rng(1).standard_normal(N); hs = np.random.default_rng(2).standard_normal(M)
L = N + M - 1
check("zero-padding to N+M-1 makes FFT product equal linear convolution",
      np.allclose(np.fft.ifft(np.fft.fft(xs, L) * np.fft.fft(hs, L)).real, np.convolve(xs, hs)))
check("direct ops 4.6e10 for 10 s / 2 s at 48 kHz", np.isclose(mc.direct_ops(480_000, 96_000), 4.6e10, rtol=0.01))
r = mc.direct_ops(480_000, 96_000) / (5 * 3 * mc.fft_ops(480_000, 96_000))
check("speedup is ~a thousand-fold with a realistic FFT constant", 100 < r < 5000)
print("NOTE: bare (N+M)log2(N+M) = %.2g, so the script's 'a few x 10^7' needs the FFT constant" % mc.fft_ops(480_000, 96_000))
sys.exit(0 if ok else 1)
