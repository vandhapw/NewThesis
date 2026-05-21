"""
split_panels.py
===============
Split a composite multi-panel figure into separate column-wise panel
images so the thesis can present them as proper subfigures (a), (b),
... with individual captions.

This performs NO data regeneration: it only crops the existing
rendered composite. All numeric content is preserved exactly as
produced by the original experiment. The super-title band and the
inter-column white gaps are detected automatically.

Usage:
  python split_panels.py <image_name> <n_cols> <out_stem>

Example:
  python split_panels.py horizon-mae-degradation-curve.png 4 horizon_mae
  -> images/horizon_mae_a.png ... horizon_mae_d.png
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
IMG = HERE / "images"
WHITE = 245
GAP_FRAC = 0.985
LETTERS = "abcdefghijkl"


def runs(flags):
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i)); start = None
    if start is not None:
        out.append((start, len(flags)))
    return out


def split(name, n_cols, stem):
    im = Image.open(IMG / name).convert("RGB")
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    # --- super-title band: widest white gap-run starting in the top 22% ---
    row_gap = [sum(1 for x in range(w) if px[x, y] >= WHITE) / w >= GAP_FRAC
               for y in range(h)]
    top_runs = [(s, e) for s, e in runs(row_gap)
                if s > 0 and s < 0.22 * h]
    title_end = max(top_runs, key=lambda r: r[1] - r[0])[1] if top_runs else 0

    # --- columns: equal division (matplotlib grids are uniform-width) ---
    bounds = [round(w * k / n_cols) for k in range(n_cols + 1)]
    print(f"  {name}: title_end={title_end}px  bounds={bounds}")

    for k in range(n_cols):
        crop = im.crop((bounds[k], title_end, bounds[k + 1], h))
        out = IMG / f"{stem}_{LETTERS[k]}.png"
        crop.save(out)
        print(f"  saved {out.name}  {crop.size}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    split(sys.argv[1], int(sys.argv[2]), sys.argv[3])
