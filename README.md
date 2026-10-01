# A Room Is a Matrix

Manim scenes for the video "A Room Is a Matrix": a room is a Toeplitz matrix,
sines are its eigenvectors, and in that basis the room is a diagonal matrix,
which is an EQ. 12 scenes (0–11), about 24 minutes as scripted.

This branch is independent of the Basel film in this repository.

## Install

```bash
sudo apt-get install -y build-essential pkg-config libcairo2-dev libpango1.0-dev \
    ffmpeg texlive texlive-latex-extra texlive-science dvisvgm
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Render

```bash
.venv/bin/python render.py            # rough cut, ~2.4 min, 480p  (default)
.venv/bin/python render.py --full     # the whole thing: ~24 min, 1080p30
.venv/bin/python render.py 05 07      # just scenes 5 and 7
.venv/bin/python render.py --scale 0.25 --quality final   # custom
```

Or open `render.py` in your editor, change `SCALE` / `QUALITY` / `SCENES` at the
top, and press Run. Output goes to `media/room/`: one file per scene, plus
`A_Room_Is_a_Matrix.mp4` with all rendered scenes joined in order.

A rough cut at 0.1 scale is meant for review and for slowing down in your
editor. `--full` is real time, so expect a long render.

## Check the numbers

```bash
.venv/bin/python verify.py
```

## Notes

- Visuals only; no audio. By-ear moments (predict, then reveal) are staged as
  waveforms and need sound added in the edit.
- Bare (N+M)log₂(N+M) is ~1.1×10⁷, so scene 11's "a few ×10⁷" only holds with
  the FFT constant; `verify.py` flags it.

## Layout

`room/config.py` palette and timing · `room/core.py` base scene and helpers ·
`room/mathcore.py` numerics · `room/scenes/act1..act4.py` the scenes.
