"""Every number the video states, computed once, so tools/verify_room.py can
check the script's claims and the scenes can draw the real thing."""

from __future__ import annotations

import numpy as np

C = 343.0  # speed of sound used for the 100 m^3 room numbers (script says 340
#            for the 3.4 m example; both appear, see verify_room)


def toeplitz_lower(h, n):
    """H[n_, k] = h[n_ - k], zero above the diagonal (causal)."""
    H = np.zeros((n, n))
    for i in range(n):
        for k in range(i + 1):
            if i - k < len(h):
                H[i, k] = h[i - k]
    return H


def circulant(h, n):
    h = np.pad(h, (0, n - len(h)))
    return np.array([[h[(i - k) % n] for k in range(n)] for i in range(n)])


def wall_h(n, tau, a):
    h = np.zeros(n)
    h[0] = 1.0
    h[tau] = a
    return h


def wall_H(omega, tau, a):
    return 1 + a * np.exp(-1j * omega * tau)


def comb_mag2(omega, tau, a):
    return 1 + a * a + 2 * a * np.cos(omega * tau)


def comb_notch_hz(tau_s, count=3):
    return [(2 * k + 1) / (2 * tau_s) for k in range(count)]


def arrival_rate(t, volume=100.0, c=C):
    return 4 * np.pi * c**3 * t**2 / volume


def t60_from_sigma(sigma):
    return np.log(1e3) / sigma


def image_sources(n_walls=2, order=3, size=(6.0, 4.0), src=(2.0, 1.5), mic=(4.0, 2.5)):
    """2-D image-source lattice for a rectangular room; returns distances."""
    Lx, Ly = size
    out = []
    for i in range(-order, order + 1):
        for j in range(-order, order + 1):
            x = i * Lx + (src[0] if i % 2 == 0 else Lx - src[0])
            y = j * Ly + (src[1] if j % 2 == 0 else Ly - src[1])
            out.append((x, y, abs(i) + abs(j)))
    return out


def regularized(Y, X, eps):
    return Y * np.conj(X) / (np.abs(X) ** 2 + eps)


def direct_ops(n, m):
    return n * m


def fft_ops(n, m):
    L = n + m - 1
    return L * np.log2(L)
