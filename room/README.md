# A Room Is a Matrix — Manim scenes

Self-contained; shares nothing with `basel/` (the Basel film). Built from the
script doc "A Room Is a Matrix": 12 scenes (0–11), ~24 min scripted.

- **Rough cut by default:** `ROOM_TIME_SCALE=0.1`, so the render is ~2.4 min.
  Slow it down in the editor, or set `ROOM_TIME_SCALE=1.0` for full length.
- **Visuals only.** No audio; the script's by-ear moments (predict/reveal) are
  staged as waveforms and need narration/sound added in the edit.

```bash
python room/render.py            # all scenes, 480p15
python room/render.py 05 07      # selected scenes
ROOM_QUALITY=final python room/render.py
python room/verify.py            # checks the numbers the script states
```

Layout: `config.py` (palette, timing), `core.py` (base scene, pacing, helpers),
`mathcore.py` (numerics), `scenes/act1..act4.py`.

Known script note: bare (N+M)log₂(N+M) is ~1.1×10⁷, so "a few ×10⁷" in scene 11
only holds with the FFT constant (3 transforms); `verify.py` flags this.
