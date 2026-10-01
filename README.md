# A Room Is an EQ

Manim scenes for the video "A Room Is an EQ": a room makes copies, copies of a
sine are still a sine, so a room is just an EQ. 11 scenes (0–10), about 18.75
minutes as scripted.

This branch is independent of every other project in this repository.

## Install (macOS)

```bash
brew install cairo pango pkg-config ffmpeg
brew install --cask mactex-no-gui        # large download; reopen Terminal after
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

(Linux: `apt-get install build-essential pkg-config libcairo2-dev libpango1.0-dev ffmpeg texlive texlive-latex-extra texlive-science dvisvgm`.)

## Render

Run from inside this folder.

```bash
.venv/bin/python render.py            # rough cut, ~1.9 min, 480p  (default)
.venv/bin/python render.py --full     # full ~19 min, 1080p30 (slow)
.venv/bin/python render.py 05 07      # just scenes 5 and 7
.venv/bin/python render.py --scale 0.25 --quality final
```

Or edit `SCALE` / `QUALITY` / `SCENES` at the top of `render.py` and press Run in
your editor. Output goes to `media/eq/`: one file per scene plus
`A_Room_Is_an_EQ.mp4` with all rendered scenes joined in order.

## Check the numbers

```bash
.venv/bin/python verify.py
```

## Notes

- Visuals only; no audio. The predict/reveal moments are staged as waveforms and
  need sound added in the edit. ODE callbacks are spoken in this video and are
  not on screen, per the script.
- The script says scene 10's counter climbs toward "ten billion"; the stated
  setup (10 s guitar, 2 s room, 48 kHz) is 4.6×10¹⁰, which is what the counter
  shows. `verify.py` notes this.
- The A/B room stamps and EQs in scene 10 are illustrative placeholders, not
  measured rooms.

## Layout

`roomeq/config.py` palette and timing · `roomeq/core.py` base scene and helpers ·
`roomeq/mathcore.py` numerics · `roomeq/scenes/act1..act4.py` the scenes.
