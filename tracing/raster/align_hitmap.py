"""
Align the 52-id hit-map SVG to a rendered muscle illustration.

Pipeline (see README.md):
  1. Render a solid silhouette of the source map (the pose/outline).
  2. Generate a clean muscle illustration conditioned on that silhouette so it
     keeps the exact pose  ->  tracing/raster/<gender>_source_2k.png
  3. This script maps each muscle path from the source SVG onto the image with a
     per-figure bbox->bbox affine (the shapes match, so this aligns every muscle
     with no smear), anchors human_body to the image corners, and writes the
     overlay SVG + the downscaled PNG asset.

Run from the repo root:
  python tracing/raster/align_hitmap.py female
Needs: pip install svgpathtools pillow numpy
"""
import re, sys
import numpy as np
from PIL import Image
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc

GENDER = sys.argv[1] if len(sys.argv) > 1 else 'female'
SRC_SVG = f'assets/maps/human_body_{GENDER}.svg' if GENDER == 'female' else 'assets/maps/human_body.svg'
IMG = f'tracing/raster/{GENDER}_source_2k.png'
OUT_SVG = f'assets/maps/human_body_{GENDER}.svg'
OUT_PNG = f'assets/maps/human_body_{GENDER}.png'
MIDX = 171.6   # x that splits the front (left) and back (right) figure

img = np.array(Image.open(IMG).convert('L')); H, W = img.shape; body = img < 235
cc = body.sum(axis=0); lo, hi = int(W * 0.42), int(W * 0.58)
split = lo + int(np.argmin(cc[lo:hi]))
xall = np.where(body.any(axis=0))[0]
def ibbox(x0, x1):
    sub = body[:, x0:x1]; ys = np.where(sub.any(axis=1))[0]; xs = np.where(sub.any(axis=0))[0]
    return x0 + xs.min(), x0 + xs.max(), ys.min(), ys.max()
IB = {'front': ibbox(xall.min(), split), 'back': ibbox(split, xall.max())}

src = open(SRC_SVG).read()
P = [(re.search(r'id="([^"]*)"', a).group(1), parse_path(d))
     for a, d in re.findall(r'<path\b(.*?)\bd="([^"]*)"\s*/?>', src, flags=re.DOTALL)
     if re.search(r'id="([^"]*)"', a)]
def sbbox(front):
    X0 = Y0 = 1e9; X1 = Y1 = -1e9
    for _, pp in P:
        for seg in pp:
            zs = (seg.start, seg.control1, seg.control2, seg.end) if isinstance(seg, CubicBezier) else (seg.start, seg.end)
            for z in zs:
                if (z.real < MIDX) == front:
                    X0 = min(X0, z.real); X1 = max(X1, z.real); Y0 = min(Y0, z.imag); Y1 = max(Y1, z.imag)
    return X0, X1, Y0, Y1
SB = {'front': sbbox(True), 'back': sbbox(False)}

def conform(z):
    f = 'front' if z.real < MIDX else 'back'
    sx0, sx1, sy0, sy1 = SB[f]; ix0, ix1, iy0, iy1 = IB[f]
    return complex(ix0 + (z.real - sx0) / (sx1 - sx0) * (ix1 - ix0),
                   iy0 + (z.imag - sy0) / (sy1 - sy0) * (iy1 - iy0))
def wseg(s):
    if isinstance(s, Line): return Line(conform(s.start), conform(s.end))
    if isinstance(s, CubicBezier): return CubicBezier(conform(s.start), conform(s.control1), conform(s.control2), conform(s.end))
    if isinstance(s, QuadraticBezier): return QuadraticBezier(conform(s.start), conform(s.control), conform(s.end))
    if isinstance(s, Arc): return Arc(conform(s.start), s.radius, s.rotation, s.large_arc, s.sweep, conform(s.end))
    return s

el = re.compile(r'<path\b(.*?)\bd="([^"]*)"\s*/?>', re.DOTALL)
out = []
for m in el.finditer(src):
    attrs = ' '.join(m.group(1).split())
    pid = re.search(r'id="([^"]*)"', attrs).group(1)
    d = Path(*[wseg(s) for s in parse_path(m.group(2))]).d()
    if pid == 'human_body':                       # anchor to image corners
        d = f'M 0,0 M {W},{H} ' + d                # -> SizeController frame == image
    out.append((attrs, d))

lines = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
         f'<svg version="1.1" id="svg1" xmlns="http://www.w3.org/2000/svg" '
         f'xmlns:svg="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
         '  <defs><style type="text/css" id="style1">.muscle{fill:#CCCCCC;fill-opacity:1;'
         'stroke:#ffffff;stroke-opacity:1;stroke-width:0.5;}</style></defs>', '  <g>']
for a, d in out:
    lines.append(f'    <path {a} d="{d}"/>')
lines += ['  </g>', '</svg>']
open(OUT_SVG, 'w').write('\n'.join(lines) + '\n')

Image.open(IMG).convert('RGB').resize((1200, int(1200 * H / W))).save(OUT_PNG)
print(f'wrote {OUT_SVG} ({len(out)} paths) and {OUT_PNG}')
