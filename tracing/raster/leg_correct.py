"""
Seat the leg muscles onto the illustration.

The bbox->bbox alignment (align_hitmap.py) lines up the torso, but the AI draws
the thighs/calves a little lower than our warped source places them, so the leg
muscles read slightly high. This nudges the leg-muscle paths down: a stretch of
everything below the hip line (so the calves drop onto the calf) plus a small
extra downward shift for the thigh muscles (which sit higher independently).

Run ONCE after align_hitmap.py (NOT idempotent — re-running double-applies):
  python tracing/raster/leg_correct.py female
  python tracing/raster/leg_correct.py male
Needs: pip install svgpathtools
"""
import re, sys
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc

GENDER = sys.argv[1] if len(sys.argv) > 1 else 'female'
SVG = ('assets/maps/human_body_female.svg' if GENDER == 'female'
       else 'assets/maps/human_body.svg')
PIVOT, SCALE, THIGH_DY = 845.0, 1.13, 45.0   # tuned against the 2304x1856 art
LEG = {'quads1', 'quads2', 'quads3', 'quads4', 'harmstrings1', 'harmstrings2',
       'calves1', 'calves2', 'calves3', 'calves4',
       'adductors1', 'adductors2', 'abductor1', 'abductor2'}
THIGH = {'quads1', 'quads2', 'quads3', 'quads4', 'adductors1', 'adductors2'}

src = open(SVG).read()
_extra = [0.0]
def warp(z):
    y = z.imag
    if y <= PIVOT:
        return z
    return complex(z.real, PIVOT + (y - PIVOT) * SCALE + _extra[0])
def ws(s):
    if isinstance(s, Line): return Line(warp(s.start), warp(s.end))
    if isinstance(s, CubicBezier): return CubicBezier(warp(s.start), warp(s.control1), warp(s.control2), warp(s.end))
    if isinstance(s, QuadraticBezier): return QuadraticBezier(warp(s.start), warp(s.control), warp(s.end))
    if isinstance(s, Arc): return Arc(warp(s.start), s.radius, s.rotation, s.large_arc, s.sweep, warp(s.end))
    return s

el = re.compile(r'<path\b(.*?)\bd="([^"]*)"\s*/?>', re.DOTALL)
out = []
for m in el.finditer(src):
    attrs = ' '.join(m.group(1).split())
    pid = re.search(r'id="([^"]*)"', attrs).group(1)
    d = m.group(2)
    if pid in LEG:
        _extra[0] = THIGH_DY if pid in THIGH else 0.0
        d = Path(*[ws(s) for s in parse_path(d)]).d()
    out.append((attrs, d))

W, H = 2304, 1856
lines = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
         f'<svg version="1.1" id="svg1" xmlns="http://www.w3.org/2000/svg" '
         f'xmlns:svg="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
         '  <defs><style type="text/css" id="style1">.muscle{fill:#CCCCCC;fill-opacity:1;'
         'stroke:#ffffff;stroke-opacity:1;stroke-width:0.5;}</style></defs>', '  <g>']
for a, d in out:
    lines.append(f'    <path {a} d="{d}"/>')
lines += ['  </g>', '</svg>']
open(SVG, 'w').write('\n'.join(lines) + '\n')
print(f'leg-corrected {SVG} ({len(out)} paths)')
