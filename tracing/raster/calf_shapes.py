"""
Replace the calf hit-regions with clean calf-shaped paths.

The inherited (warped male) calf geometry doesn't match where the AI draws the
gastrocnemius, so the calves read as scattered/floating slivers. This swaps
calves1-4 for four leaf shapes (two heads per lower leg) seated on the calf
belly, tapering toward the Achilles. Per-gender positions because the two
illustrations stand slightly differently.

Run ONCE after align_hitmap.py / leg_correct.py (NOT idempotent):
  python tracing/raster/calf_shapes.py female
  python tracing/raster/calf_shapes.py male
Needs: pip install svgpathtools  (only re/PIL-free; no rendering)
"""
import re, sys

GENDER = sys.argv[1] if len(sys.argv) > 1 else 'female'
SVG = ('assets/maps/human_body_female.svg' if GENDER == 'female'
       else 'assets/maps/human_body.svg')

# tuned against the 2304x1856 illustrations (Lx/Rx = each lower-leg centre)
PARAMS = {
    'female': dict(Lx=1618, Rx=1868, sep=8, ytop=1260, h=250, wo=44, wi=48, drop=6),
    'male':   dict(Lx=1500, Rx=1842, sep=8, ytop=1338, h=215, wo=43, wi=47, drop=6),
}[GENDER]

def calf(cx, ytop, w, h):
    """A leaf: rounded top, widest ~a third down, tapering to a point (Achilles)."""
    ymid = ytop + h * 0.34
    ybot = ytop + h
    return (f'M {cx:.1f},{ytop:.1f} '
            f'C {cx+w*0.72:.1f},{ytop:.1f} {cx+w:.1f},{ymid-h*0.14:.1f} {cx+w:.1f},{ymid:.1f} '
            f'C {cx+w:.1f},{ymid+h*0.22:.1f} {cx+w*0.42:.1f},{ybot:.1f} {cx:.1f},{ybot:.1f} '
            f'C {cx-w*0.42:.1f},{ybot:.1f} {cx-w:.1f},{ymid+h*0.22:.1f} {cx-w:.1f},{ymid:.1f} '
            f'C {cx-w:.1f},{ymid-h*0.14:.1f} {cx-w*0.72:.1f},{ytop:.1f} {cx:.1f},{ytop:.1f} Z')

p = PARAMS
CALVES = {
    'calves1': calf(p['Lx'] - p['sep'], p['ytop'],            p['wo'], p['h'] - 12),  # left outer
    'calves2': calf(p['Lx'] + p['sep'], p['ytop'] + p['drop'], p['wi'], p['h']),       # left inner
    'calves3': calf(p['Rx'] + p['sep'], p['ytop'],            p['wo'], p['h'] - 12),  # right outer
    'calves4': calf(p['Rx'] - p['sep'], p['ytop'] + p['drop'], p['wi'], p['h']),       # right inner
}

src = open(SVG).read()
el = re.compile(r'(<path\b)(.*?)(\bd=")([^"]*)("\s*/?>)', re.DOTALL)
def repl(m):
    pid = re.search(r'id="([^"]*)"', m.group(2))
    if pid and pid.group(1) in CALVES:
        return m.group(1) + m.group(2) + m.group(3) + CALVES[pid.group(1)] + m.group(5)
    return m.group(0)
open(SVG, 'w').write(el.sub(repl, src))
print(f'reshaped calves in {SVG}')
