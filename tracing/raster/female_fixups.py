"""
Per-muscle fixups for the FEMALE map where the warped source lands a muscle off
the illustration: the neck sat on the chin, and the deltoids sat inboard on the
clavicle / upper trapezius. Each fixup is an affine (scale about a pivot + shift)
applied to one muscle group's paths.

Run ONCE after align_hitmap.py / leg_correct.py (NOT idempotent):
  python tracing/raster/female_fixups.py
Needs: pip install svgpathtools
"""
import re
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc

SVG = 'assets/maps/human_body_female.svg'

# id-group -> (pivot_x, pivot_y, scale_x, scale_y, dx, dy)
FIXUPS = [
    (['neck'],                     572, 371, 1.0,  0.80, 0,  26),  # down onto the throat
    (['shoulder1', 'shoulder2'],   564, 425, 1.32, 1.0,  0,  22),  # front delts out+down
    (['shoulder3', 'shoulder4'],  1712, 385, 1.42, 1.0,  0,  60),  # rear delts out+down
]

src = open(SVG).read()
def transform(d, px, py, sx, sy, dx, dy):
    def w(z):
        return complex(px + (z.real - px) * sx + dx, py + (z.imag - py) * sy + dy)
    def ws(s):
        if isinstance(s, Line): return Line(w(s.start), w(s.end))
        if isinstance(s, CubicBezier): return CubicBezier(w(s.start), w(s.control1), w(s.control2), w(s.end))
        if isinstance(s, QuadraticBezier): return QuadraticBezier(w(s.start), w(s.control), w(s.end))
        if isinstance(s, Arc): return Arc(w(s.start), s.radius, s.rotation, s.large_arc, s.sweep, w(s.end))
        return s
    return Path(*[ws(s) for s in parse_path(d)]).d()

lookup = {}
for ids, *params in FIXUPS:
    for i in ids:
        lookup[i] = params

el = re.compile(r'(<path\b)(.*?)(\bd=")([^"]*)("\s*/?>)', re.DOTALL)
def repl(m):
    pid = re.search(r'id="([^"]*)"', m.group(2))
    if pid and pid.group(1) in lookup:
        return m.group(1) + m.group(2) + m.group(3) + transform(m.group(4), *lookup[pid.group(1)]) + m.group(5)
    return m.group(0)
open(SVG, 'w').write(el.sub(repl, src))
print(f'applied {len(FIXUPS)} fixups to {SVG}')
