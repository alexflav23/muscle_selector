"""
Slim the female figure. The generated illustration came out too thick/muscular,
so squeeze each figure horizontally toward its own vertical axis by FACTOR. The
SAME squeeze is applied to the illustration (PNG) and to every muscle hit-path
(SVG), so the highlight alignment is preserved. human_body's full-image anchor
rect is left untouched so mapSize still equals the image.

Run ONCE after the other steps (NOT idempotent):
  python tracing/raster/slim_female.py [factor]   # default 0.80
Needs: pip install svgpathtools pillow numpy
"""
import re, sys
import numpy as np
from PIL import Image, ImageDraw
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc

FACTOR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.80
PNG = 'assets/maps/human_body_female.png'
SVG = 'assets/maps/human_body_female.svg'
W, H = 2304, 1856
FAXIS, BAXIS, SPLIT = 563.0, 1713.0, 1135.0   # front axis, back axis, figure gap
def axis_of(x):
    return FAXIS if x < SPLIT else BAXIS

# image: per-figure horizontal squeeze, white elsewhere
img = np.array(Image.open(PNG).convert('RGB').resize((W, H)))
out = np.full_like(img, 255)
for ox in range(W):
    ax = axis_of(ox)
    sx = ax + (ox - ax) / FACTOR
    if 0 <= sx < W:
        out[:, ox] = img[:, int(round(sx))]
slim = Image.fromarray(out)
ImageDraw.Draw(slim).rectangle([int(W * 0.475), 0, int(W * 0.525), H], fill=(255, 255, 255))  # tidy the gap
slim.save(PNG)

# svg: squeeze every muscle path (keep human_body's anchor rect)
def warp(z):
    ax = axis_of(z.real)
    return complex(ax + (z.real - ax) * FACTOR, z.imag)
def ws(s):
    if isinstance(s, Line): return Line(warp(s.start), warp(s.end))
    if isinstance(s, CubicBezier): return CubicBezier(warp(s.start), warp(s.control1), warp(s.control2), warp(s.end))
    if isinstance(s, QuadraticBezier): return QuadraticBezier(warp(s.start), warp(s.control), warp(s.end))
    if isinstance(s, Arc): return Arc(warp(s.start), s.radius, s.rotation, s.large_arc, s.sweep, warp(s.end))
    return s
src = open(SVG).read()
el = re.compile(r'(<path\b)(.*?)(\bd=")([^"]*)("\s*/?>)', re.DOTALL)
def repl(m):
    if re.search(r'id="([^"]*)"', m.group(2)).group(1) == 'human_body':
        return m.group(0)
    return m.group(1) + m.group(2) + m.group(3) + Path(*[ws(s) for s in parse_path(m.group(4))]).d() + m.group(5)
open(SVG, 'w').write(el.sub(repl, src))
print(f'slimmed female by {FACTOR}')
