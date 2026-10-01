"""Act III -- Diagonalize the room (scenes 7-10)."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, Dot, FadeIn, FadeOut,
    Line, NumberPlane, Rectangle, Text, Transform, VGroup, ValueTracker, Write,
    always_redraw,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from room.config import CORAL, ECHO, EIGEN, GHOST, INK, INK_DIM, ODE, SIGNAL, STAMP  # noqa: E402
from room.core import (  # noqa: E402
    RoomScene, curve_on, head, matrix_grid, ode_note, say, tex,
)
from room import mathcore as mc  # noqa: E402


def arrows_column(n, omega, size=0.28, color=SIGNAL, x=0.0, y0=1.6, gap=0.5, phase=0.0):
    out = VGroup()
    for i in range(n):
        z = np.exp(1j * (omega * i + phase))
        c = np.array([x, y0 - i * gap, 0])
        out.add(Arrow(c, c + size * np.array([z.real, z.imag, 0]), buff=0,
                      stroke_width=3, color=color, max_tip_length_to_length_ratio=0.5))
    return out


class Scene07Eigenvectors(RoomScene):
    scene_id = "07"

    def construct(self):
        p = self.pacer
        self.add(head("Sines are eigenvectors"))
        n, omega = 6, 0.9
        h = np.array([1.0, 0.0, 0.0, 0.6])
        H = mc.toeplitz_lower(h, n)
        grid = matrix_grid(H, cell=0.5).shift(LEFT * 3.4 + DOWN * 0.2)
        e_in = arrows_column(n, omega, x=0.0, y0=1.25, gap=0.5).next_to(grid, RIGHT, buff=0.7)
        # the actual product, as arrows (truncate the causal edge: rows >= len(h))
        y = H @ np.exp(1j * omega * np.arange(n))
        lam = mc.wall_H(omega, 3, 0.6)
        out_col = VGroup()
        for i in range(n):
            c = e_in[i].get_start() + RIGHT * 1.6
            out_col.add(Arrow(c, c + 0.28 * np.array([y[i].real, y[i].imag, 0]), buff=0,
                              stroke_width=3, color=EIGEN,
                              max_tip_length_to_length_ratio=0.5))
        lbl_in = Text("e^{iωn}", font_size=20, color=SIGNAL).next_to(e_in, UP, buff=0.2)
        lbl_out = Text("H·e^{iωn}", font_size=20, color=EIGEN).next_to(out_col, UP, buff=0.2)

        def visual(rt):
            self.play(FadeIn(grid), FadeIn(e_in), FadeIn(lbl_in), run_time=rt / 4)
            self.play(FadeIn(out_col), FadeIn(lbl_out), run_time=rt / 3)
        p.beat(0.4, visual)

        note = say("each row gives the same arrow, rotated one more step", size=20)
        deriv = tex(r"\sum_k h[n-k]\,e^{i\omega k}=e^{i\omega n}"
                    r"\underbrace{\sum_m h[m]\,e^{-i\omega m}}_{H(\omega)}",
                    size=30).to_edge(RIGHT, buff=0.4).shift(UP * 1.4)
        name = tex(r"\mathbf{H}\,e_\omega=H(\omega)\,e_\omega", size=36, color=EIGEN
                   ).next_to(deriv, DOWN, buff=0.6)
        p.beat(0.6, lambda rt: (self.play(FadeIn(note), Write(deriv), run_time=rt / 2)))
        p.beat(0.75, lambda rt: self.play(Write(name), run_time=rt / 2))

        hook = ode_note(r"\text{ODEs: guess } e^{rt},\ \tfrac{d}{dt}e^{rt}=re^{rt}", size=24
                        ).next_to(name, DOWN, buff=0.5)
        cont = tex(r"e^{st}\mapsto H(s)e^{st},\quad H(s)=1+a\,e^{-s\tau}", size=26,
                   color=STAMP).next_to(hook, DOWN, buff=0.3)
        p.beat(1.0, lambda rt: (self.play(Write(hook), run_time=rt / 3),
                                self.play(Write(cont), run_time=rt / 3)))


class Scene08ChangeBasis(RoomScene):
    scene_id = "08"

    def construct(self):
        p = self.pacer
        self.add(head("Change basis and the room becomes an EQ"))
        hook = ode_note(r"x'=Ax,\quad A=PDP^{-1}\ \Rightarrow\ \text{decoupled scalar equations}",
                        size=28).shift(UP * 2.4)
        same = Text("Same move, on a room.", font_size=22, color=INK_DIM
                    ).next_to(hook, DOWN, buff=0.25)
        p.beat(0.15, lambda rt: (self.play(Write(hook), run_time=rt / 2), self.play(FadeIn(same), run_time=rt / 4)))

        # F  ->  Lambda  ->  F^-1
        stage_y = 0.3
        f_box = Rectangle(width=2.2, height=1.8, stroke_color=SIGNAL).shift(LEFT * 4.2 + UP * stage_y)
        f_txt = tex(r"\mathbf{F}", size=44, color=SIGNAL).move_to(f_box)
        l_box = Rectangle(width=2.6, height=1.8, stroke_color=EIGEN).shift(UP * stage_y)
        # sliders = the diagonal of Lambda
        sliders = VGroup()
        rng = np.random.default_rng(5)
        mags = [0.9, 0.5, 0.75, 0.3, 0.6]
        for i, m in enumerate(mags):
            x = -0.9 + 0.45 * i
            sliders.add(Line([x, stage_y - 0.7, 0], [x, stage_y + 0.7, 0], stroke_width=2,
                             color=GHOST))
            sliders.add(Dot([x, stage_y - 0.7 + 1.4 * m, 0], radius=0.09, color=EIGEN))
        l_txt = tex(r"\boldsymbol{\Lambda}", size=44, color=EIGEN).next_to(l_box, UP, buff=0.1)
        fi_box = Rectangle(width=2.2, height=1.8, stroke_color=STAMP).shift(RIGHT * 4.2 + UP * stage_y)
        fi_txt = tex(r"\mathbf{F}^{-1}", size=44, color=STAMP).move_to(fi_box)
        a1 = Arrow(f_box.get_right(), l_box.get_left(), buff=0.1, color=INK_DIM)
        a2 = Arrow(l_box.get_right(), fi_box.get_left(), buff=0.1, color=INK_DIM)
        c1 = Text("the guitar splits into frequencies", font_size=17, color=INK_DIM
                  ).next_to(f_box, DOWN, buff=0.2)
        c2 = Text("each scaled and rotated on its own", font_size=17, color=INK_DIM
                  ).next_to(l_box, DOWN, buff=0.2)
        c3 = Text("recombine: the stairwell guitar", font_size=17, color=INK_DIM
                  ).next_to(fi_box, DOWN, buff=0.2)

        def stages(rt):
            self.play(Create(f_box), Write(f_txt), FadeIn(c1), run_time=rt / 6)
            self.play(Create(a1), Create(l_box), FadeIn(sliders), Write(l_txt), FadeIn(c2), run_time=rt / 5)
            self.play(Create(a2), Create(fi_box), Write(fi_txt), FadeIn(c3), run_time=rt / 6)
        p.beat(0.5, stages)

        fact = tex(r"\mathbf{H}=\mathbf{F}^{-1}\boldsymbol{\Lambda}\mathbf{F},\quad "
                   r"\boldsymbol{\Lambda}=\mathrm{diag}\big(H(\omega_0),H(\omega_1),\dots\big)",
                   size=30).shift(DOWN * 1.6)
        conv = tex(r"Y(\omega)=H(\omega)\,X(\omega)", size=36, color=EIGEN).next_to(fact, DOWN, buff=0.35)
        lap = ode_note(r"\mathcal{L}\{f*g\}=F(s)G(s)\ \text{ --- that line was a diagonalization}",
                       size=22).next_to(conv, DOWN, buff=0.3)
        p.beat(0.7, lambda rt: self.play(Write(fact), run_time=rt / 2))
        p.beat(0.82, lambda rt: (self.play(Write(conv), run_time=rt / 3), self.play(Write(lap), run_time=rt / 3)))

        # s -> i omega, then polar form
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.mobjects[0]], run_time=0.5) if False else None
        polar = tex(r"H(i\omega)=|H(\omega)|\,e^{i\phi(\omega)}", size=34, color=EIGEN
                    ).to_edge(RIGHT, buff=0.6).shift(UP * 2.1)
        sip = Text("s → iω allowed because ∫|h| < ∞", font_size=18, color=INK_DIM).next_to(polar, DOWN)
        osc = ode_note(r"\text{forced oscillator: gain and phase lag}", size=22).next_to(sip, DOWN, buff=0.2)
        p.beat(1.0, lambda rt: (self.play(Write(polar), FadeIn(sip), run_time=rt / 3),
                                self.play(Write(osc), run_time=rt / 4)))


class Scene09Comb(RoomScene):
    scene_id = "09"

    def construct(self):
        p = self.pacer
        self.add(head("One wall's eigenvalues: the comb"))
        a, tau = 0.6, 0.010
        plane = NumberPlane(x_range=[-1, 2.6, 1], y_range=[-1.6, 1.6, 1], x_length=4.6,
                            y_length=3.2, background_line_style={"stroke_opacity": 0.25,
                                                                 "stroke_color": INK_DIM},
                            axis_config={"stroke_color": INK_DIM}).shift(LEFT * 4.0 + DOWN * 0.3)
        w = ValueTracker(0.0)
        circ = Circle(radius=a * plane.get_x_unit_size(), stroke_color=GHOST, stroke_width=2
                      ).move_to(plane.c2p(1, 0))
        dot = always_redraw(lambda: Dot(plane.c2p(*[
            1 + a * np.cos(-w.get_value()), a * np.sin(-w.get_value())]), color=EIGEN, radius=0.1))
        radius = always_redraw(lambda: Line(plane.c2p(0, 0), dot.get_center(), color=EIGEN))
        form = tex(r"H(\omega)=1+a\,e^{-i\omega\tau}", size=32).next_to(plane, UP, buff=0.4)

        ax = Axes(x_range=[0, 300, 100], y_range=[0, 1.8, 1], x_length=5.4, y_length=2.6,
                  axis_config={"color": INK_DIM, "include_ticks": False}
                  ).shift(RIGHT * 3.4 + DOWN * 0.1)
        fs = np.linspace(0, 300, 300)
        mag = np.sqrt(mc.comb_mag2(2 * np.pi * fs, tau, a))
        curve = curve_on(ax, fs, mag, EIGEN)
        # the dot's angle w = omega*tau; map the full sweep to 0..300 Hz
        cursor = always_redraw(lambda: Line(
            ax.c2p(w.get_value() / (2 * np.pi * tau), 0),
            ax.c2p(w.get_value() / (2 * np.pi * tau), 1.8), color=STAMP, stroke_width=2))
        notches = VGroup(*[Text(f"{int(f)} Hz", font_size=16, color=CORAL
                                ).next_to(ax.c2p(f, 0), DOWN, buff=0.15)
                           for f in mc.comb_notch_hz(tau)])
        depth = tex(r"|H|^2=1+a^2+2a\cos(\omega\tau)", size=28).next_to(ax, UP, buff=0.4)

        def build(rt):
            self.play(FadeIn(plane), Create(circ), Write(form), run_time=rt / 5)
            self.play(FadeIn(ax), Create(curve), Write(depth), FadeIn(dot), FadeIn(radius),
                      FadeIn(cursor), run_time=rt / 5)
        p.beat(0.3, build)
        p.beat(0.8, lambda rt: self.play(w.animate.set_value(2 * np.pi * tau * 300),
                                         run_time=rt, rate_func=lambda t: t))
        note = Text(f"notches at f = (2k+1)/2τ: 50, 150, 250 Hz   |   depth 1−a, peaks 1+a",
                    font_size=19, color=INK_DIM).to_edge(DOWN, buff=1.3)
        p.beat(1.0, lambda rt: self.play(FadeIn(notches), FadeIn(note), run_time=min(1.5, rt)))


class Scene10Poles(RoomScene):
    scene_id = "10"

    def construct(self):
        p = self.pacer
        self.add(head("Poles: singing in the shower"))
        sigma = ValueTracker(1.2)
        wd = 3.0
        sp = NumberPlane(x_range=[-3, 1, 1], y_range=[-4, 4, 2], x_length=3.4, y_length=3.4,
                         background_line_style={"stroke_opacity": 0.2, "stroke_color": INK_DIM},
                         axis_config={"stroke_color": INK_DIM}).shift(LEFT * 5 + DOWN * 0.4)
        pole = lambda s: Dot(sp.c2p(-s, wd), color=CORAL, radius=0.09)  # noqa: E731
        poles = always_redraw(lambda: VGroup(pole(sigma.get_value()),
                                             Dot(sp.c2p(-sigma.get_value(), -wd), color=CORAL, radius=0.09)))
        ax_eq = Axes(x_range=[0, 6, 2], y_range=[0, 4, 2], x_length=3.8, y_length=2.4,
                     axis_config={"color": INK_DIM, "include_ticks": False}).shift(DOWN * 0.1)
        ax_h = Axes(x_range=[0, 6, 2], y_range=[-1, 1, 1], x_length=3.8, y_length=2.4,
                    axis_config={"color": INK_DIM, "include_ticks": False}).shift(RIGHT * 4.6 + DOWN * 0.1)
        ws = np.linspace(0, 6, 300)
        eq_curve = always_redraw(lambda: curve_on(
            ax_eq, ws, 1 / np.sqrt((wd**2 + sigma.get_value()**2 - ws**2) ** 2
                                   + (2 * sigma.get_value() * ws) ** 2) * 4, EIGEN))
        ts = np.linspace(0, 6, 300)
        h_curve = always_redraw(lambda: curve_on(
            ax_h, ts, np.exp(-sigma.get_value() * ts) * np.sin(wd * ts), STAMP))
        lbls = VGroup(Text("s-plane", font_size=18, color=INK_DIM).next_to(sp, UP),
                      Text("|H| (the EQ)", font_size=18, color=INK_DIM).next_to(ax_eq, UP),
                      Text("h(t)", font_size=18, color=INK_DIM).next_to(ax_h, UP))
        form = tex(r"H(s)=\frac{1}{ms^2+cs+k},\ s=-\sigma\pm i\omega_d,\ \sigma=\frac{c}{2m}",
                   size=26).to_edge(DOWN, buff=1.4)
        p.beat(0.3, lambda rt: self.play(FadeIn(sp), FadeIn(ax_eq), FadeIn(ax_h), FadeIn(poles),
                                         FadeIn(eq_curve), FadeIn(h_curve), FadeIn(lbls),
                                         Write(form), run_time=min(rt, 2)))
        p.beat(0.7, lambda rt: self.play(sigma.animate.set_value(0.25), run_time=rt))
        link = tex(r"T_{60}\approx\frac{6.9}{\sigma},\quad \text{peak width}\approx\frac{\sigma}{\pi}\,\text{Hz}",
                   size=26, color=STAMP).next_to(form, UP, buff=0.3)
        gag = ode_note(r"\text{mass-spring-damper; a swing pushed at the right rhythm}", size=20
                       ).to_edge(DOWN, buff=0.8)
        p.beat(1.0, lambda rt: (self.play(Write(link), run_time=rt / 3), self.play(FadeIn(gag), run_time=rt / 4)))
