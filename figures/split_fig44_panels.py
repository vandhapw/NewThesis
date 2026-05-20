"""
split_fig44_panels.py
=====================
Split the composite 2x2 figure `model-performance-lstm-tgcn-hybrid.png`
into four separate panel images so the thesis can present them as
proper subfigures (a)-(d) with individual captions.

This performs NO data regeneration: it only crops the existing
rendered composite. All numeric content is preserved exactly as
produced by the original experiment. Panel and row/column boundaries
are detected automatically from the white gaps in the figure, so the
split adapts if the source image changes.

Panels:
  (a) top-left     -> R^2 score per feature
  (b) top-right    -> MSE per feature
  (c) bottom-left  -> aggregate metrics
  (d) bottom-right -> training loss convergence

Usage:
  python split_fig44_panels.py
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "images" / "model-performance-lstm-tgcn-hybrid.png"
WHITE = 245          # >= this grey value counts as background
GAP_FRAC = 0.985     # row/col is a "gap" if this fraction of pixels is white


def white_fraction(line):
    return sum(1 for p in line if p >= WHITE) / len(line)


def runs_of_gaps(is_gap):
    """Return [(start, end)] index ranges where is_gap is True."""
    runs, start = [], None
    for i, g in enumerate(is_gap):
        if g and start is None:
            start = i
        elif not g and start is not None:
            runs.append((start, i)); start = None
    if start is not None:
        runs.append((start, len(is_gap)))
    return runs


def main():
    im = Image.open(SRC).convert("RGB")
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    row_gap = [white_fraction([px[x, y] for x in range(w)]) >= GAP_FRAC
               for y in range(h)]
    col_gap = [white_fraction([px[x, y] for y in range(h)]) >= GAP_FRAC
               for x in range(w)]

    # Title band: the first gap run that does NOT start at the very top
    # (the run at y=0 is the page margin) marks the end of the super-title.
    title_end = 0
    for s, e in runs_of_gaps(row_gap):
        if s > 0 and s < 0.20 * h:
            title_end = e
            break

    # Row split: widest gap run whose centre lies in the middle 40-65% band
    # (the inter-row whitespace, not the narrow axis-label gaps).
    row_runs = sorted(
        [(s, e) for s, e in runs_of_gaps(row_gap)
         if 0.40 * h < (s + e) / 2 < 0.65 * h],
        key=lambda r: r[1] - r[0], reverse=True)
    midy = (sum(row_runs[0]) // 2 if row_runs else h // 2)

    # Column split: longest gap run with centre in the middle 35-65% band.
    col_runs = sorted(
        [(s, e) for s, e in runs_of_gaps(col_gap)
         if 0.35 * w < (s + e) / 2 < 0.65 * w],
        key=lambda r: r[1] - r[0], reverse=True)
    midx = (sum(col_runs[0]) // 2 if col_runs else w // 2)

    print(f"  detected: title_end={title_end}px  midx={midx}px  midy={midy}px")

    panels = {
        "a": (0,    title_end, midx, midy),
        "b": (midx, title_end, w,    midy),
        "c": (0,    midy,      midx, h),
        "d": (midx, midy,      w,    h),
    }
    for tag, box in panels.items():
        out = HERE / "images" / f"fig44_model_perf_{tag}.png"
        crop = im.crop(box)
        crop.save(out)
        print(f"  saved {out.name}  {crop.size}")


if __name__ == "__main__":
    main()
