# Basel Problem — Manim production (flux layer)

A visual explanation of the complex-analytic Basel proof, built to the
120-second ten-scene brief. Every complex contribution is read as an **along**
part (circulation — the coaster's work) and an **across** part (flux — fluid
leaking through the path).

## Status

**Scenes 1–6 are implemented, rendered and verified. Scenes 7–10 are not yet
written.** The timing map, the maths, and all shared helpers already cover all
ten scenes; what is missing is the six scene modules' worth of staging for
scenes 7–10 and the assembled overview.

| Scene | Interval | s | Module | State |
|---|---|---|---|---|
| 01 The mystery | 00:00–00:08 | 8 | `basel/scenes/s01_mystery.py` | rendered, 8.000 s |
| 02 Coaster energy | 00:08–00:21 | 13 | `basel/scenes/s02_coaster.py` | rendered, 13.000 s |
| 03 Path independence | 00:21–00:31 | 10 | `basel/scenes/s03_path_independence.py` | rendered, 10.000 s |
| 04 Along and across | 00:31–00:47 | 16 | `basel/scenes/s04_accumulation.py` | rendered, 16.000 s |
| 05 A hole, a sprinkler, 2πi | 00:47–01:02 | 15 | `basel/scenes/s05_sprinkler.py` | rendered, 15.000 s |
| 06 Why residues survive | 01:02–01:16 | 14 | `basel/scenes/s06_residues.py` | rendered, 14.000 s |
| 07 Design the Basel function | 01:16–01:29 | 13 | — | not written |
| 08 The residue at zero | 01:29–01:40 | 11 | — | not written |
| 09 The boundary vanishes | 01:40–01:53 | 13 | — | not written |
| 10 Resolve the sum | 01:53–02:00 | 7 | — | not written |

Measured durations are from `ffprobe` on the rendered files, not from intended
run times. The six built scenes total **76 s** of the 120 s map.

## The one flux rule

The fluid on screen is always `P = conj(f)`, never `f`. With that fluid,
`f(z) dz = (along + i·across)·|dz|`, so a contour integral's real part is the
circulation of `P` and its imaginary part is the flux of `P` out of the curve
(measured to the right of travel, which is outward on a counterclockwise loop).
`basel/flux.py` enforces this: `FlowField.of(...)` conjugates for you, and the
only way to draw `f` itself is `FlowField.raw(...)`, which scene 5 uses for two
seconds precisely to motivate the flip.

## Install

Tested on Linux, Python 3.11.15, Manim Community **0.21.0** (Cairo renderer),
ffmpeg 6.x, TeX Live (`latex` + `dvisvgm`).

```bash
sudo apt-get install -y build-essential pkg-config libcairo2-dev \
    libpango1.0-dev ffmpeg texlive texlive-latex-extra texlive-science dvisvgm
python3 -m venv .venv
.venv/bin/pip install -U pip setuptools wheel
.venv/bin/pip install -r requirements.txt
```

A virtualenv is not optional on Debian/Ubuntu: installing into the
distro-managed `site-packages` fails on `srt` and `wheel`.

## Verify before rendering

```bash
.venv/bin/python tools/verify_math.py
```

75 checks, all passing: energy conservation and closed-loop work on the
coaster; both routes' work equal to `U(A) − U(B)`; `f dz = (along + i·across)|dz|`
at sampled steps; circulation and flux zero for `f(z)=z`; flux `2π` at every
radius for `1/z`; zero flux and a `cos t` outward component for `1/z²`;
residues `1/n²` at the nonzero integers and `−π²/3` at the origin; the squares
`C_N` purely imaginary and matching `2πi·Σ Res`; `|cot(πz)| ≤ 2` on those
squares; particles moving along `conj(f)` and never through a pole.

## Render

### From Wing IDE (no command line, no `manim` on PATH)

Open **`render.py`** and press Run. That is the whole procedure. It imports
manim as a library and drives the renderer itself, so the `manim` command does
not need to exist on your PATH.

Edit the settings at the top of the file, then Run again:

```python
QUALITY = "draft"      # "draft" = 854x480 @ 15 fps,  "final" = 1920x1080 @ 60 fps
SCENES  = "all"        # or a list, e.g. ["04", "05"]
VERIFY_FIRST = True    # run the 75 maths checks before rendering
OPEN_WHEN_DONE = False # True asks your OS to open each finished video
```

`render.py` puts its own folder on `sys.path`, so Wing's working directory does
not matter — it only has to sit beside the `basel/` folder.

**If it says manim does not exist**, it is almost always that Wing is using a
different interpreter from the one manim is installed for. `render.py` prints
the exact interpreter path it is running under and the exact `pip install`
command for *that* interpreter. To point Wing at the virtualenv instead:
*Project → Project Properties → Python Executable → Custom*, and choose
`.venv/bin/python` (`.venv\Scripts\python.exe` on Windows).

It also checks for `ffmpeg` and `latex` up front and names the install command
for your platform, since a missing TeX distribution otherwise fails deep inside
the first equation.

### From a terminal

```bash
python render.py              # same thing, same settings
./render.sh draft             # 480p, 15 fps
./render.sh final             # 1920x1080, 60 fps
```

Or one scene at a time through the manim CLI, if you have it — this is the
draft command, `-pql` at 15 fps:

```bash
.venv/bin/python -m manim render -pql --fps 15 basel/scenes/s04_accumulation.py Scene04Accumulation
```

Drop `-p` to skip opening the player (headless machines). Note `python -m manim`
works even when the bare `manim` command is not on PATH.

1080p final for one scene:

```bash
.venv/bin/python -m manim render -qh --fps 60 -r 1920,1080 \
    basel/scenes/s05_sprinkler.py Scene05Sprinkler
```

Output lands in `media/videos/`.

## Retiming

`basel/config.py` is the single configuration block. Scenes are stored as
named beats with relative weights, so a longer cut is a per-scene override, not
uniform slow motion:

```python
SCENE_DURATION_OVERRIDES = {"04": 40.0}   # only scene 4 stretches
```

`NARRATOR_PAUSE` is kept separate from drawing speed. No narration is
synthesised and no voiceover plugin is required; the film is usable silently.

## Two implementation notes worth knowing

Both were found by inspecting rendered frames, not by reading the API.

- **Frame-exact timing.** Manim renders `ceil(run_time × fps)` frames per
  animation, so any run_time that is not a whole number of frames makes the
  written file longer than the scene's internal clock — at 15 fps that drifted
  a scene 0.27 s. `BaselScene` quantises every `play` and `wait` to whole
  frames, which is why measured durations land on the map exactly.
- **Live readouts.** Manim bakes every mobject sitting before the first *moving*
  mobject into a static cached image for the duration of a `play`, so a readout
  mutated from another mobject's updater silently renders its old value.
  `DigitReadout` (in `basel/helpers.py`) pre-builds all ten digits per slot and
  only toggles opacity — no LaTeX compiled and no text constructed per frame —
  and every live readout carries its own updater.

## Known limitations

- Scenes 7–10 and the assembled 120 s overview are not implemented.
- Frames were inspected at 480p15; a 1080p pass has not been run, so
  final-resolution label sizing is unverified.
- `basel/flux.py` compresses arrow lengths (`magnitude / (magnitude + knee)`)
  so near-pole arrows stay drawable. Arrow **direction** is exact; arrow
  **length** is indicative, not a speed reading.
- The particle puffs described for scene 7 are illustrative of relative faucet
  strength only, and are not claimed to be the exact conjugate field near every
  pole.
