#!/usr/bin/env python3
"""Check the numbers the script states."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from roomeq import mathcore as mc

ok = True
def check(name, cond):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

check("3.4 m / 340 m/s = 10 ms", np.isclose(3.4 / 340, 0.010))
check("comb notches 50/150/250 Hz (every 100 Hz) for a 10 ms echo",
      np.allclose(mc.comb_notch_hz(0.010), [50, 150, 250]))
check("comb notch is silent-ish: |H| = 1-a at the notch",
      np.isclose(abs(mc.phasor_sum([0, .010], [1, .6], 50.0)[1]), 0.4))
amp, _ = mc.sine_shift_add_is_sine()
check("shifted copies of a sine add into a sine (closed-form phasor)", amp > 0)
h = np.array([1, 0, .6, 0, .3]); x = np.random.default_rng(0).standard_normal(7)
M = len(x) + len(h) - 1
G = np.zeros((7, M))
for k in range(7):
    for j, hv in enumerate(h):
        G[k, k + j] = x[k] * hv
check("grid column sums equal np.convolve (scene 5)", np.allclose(G.sum(0), np.convolve(x, h)))
check("EQ route: Y = H X after zero padding",
      np.allclose(np.fft.ifft(np.fft.fft(x, M) * np.fft.fft(h, M)).real, np.convolve(x, h)))
n = mc.direct_conv_ops(10, 2, 48000)
check("10 s guitar x 2 s room at 48 kHz = 4.6e10 multiplications", np.isclose(n, 4.6e10, rtol=0.01))
print("NOTE: the script says 'ten billion'; at 48 kHz it is 4.6e10. At 16 kHz it is 5.1e9. "
      "The scene counter shows the true 48 kHz figure.")
sys.exit(0 if ok else 1)
