"""
Derive the female muscle map from the male map. Three stages, all reproducible:

  1. A 2D anatomical warp about each figure's vertical axis: a global SLIM(y)
     narrows the broad male shoulders and slims the limbs, and a core-only
     BOOST(y) adds the waist pinch and hip/pelvis flare (faded out with
     distance-from-axis so the hands never flare with the hips).
  2. The flat male pectorals (chest1/chest2) are replaced with breast shapes.
  3. The male hairstyle is swapped for line-art feminine hair (forehead hairline
     + side-framing locks on the front, a fuller mass on the back).

Stages 2-3 reshape geometry only inside existing paths -- no id/title/class is
renamed, added, or removed -- so the female map stays a drop-in for the male one
and the 52-id contract (F7-F9) holds. The warp moves only x, preserving vertical
registration. The result is a clearly-female *scaffold*; see TRACING.md for the
publication-grade hand-trace.

Run from the repo root:  python tracing/derive_female_scaffold.py
Needs: pip install svgpathtools cairosvg
Writes: assets/maps/human_body_female.svg  +  tracing/human_body_female.scaffold.svg
"""
import re
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc

src = open('assets/maps/human_body.svg').read()
FRONT_AXIS, BACK_AXIS, MIDX = 88.5, 254.0, 171.6

# 2D anatomical warp: new_x = axis + dx * SLIM(y) * effective_boost(dx, y)
#   SLIM(y)  - global narrowing applied to EVERY point: pulls in the broad male
#              shoulders and slims the arms/legs as a whole.
#   BOOST(y) - extra sculpting applied ONLY to the torso core (small |dx|): the
#              waist pinch and the hip/pelvis flare that read as female.
# The boost fades to 1.0 with distance-from-axis (CORE_OUT..LIMB), so the off-axis
# hands and wrists keep following SLIM and never flare out with the hips. Because
# only x moves (as a function of x and y), every id and the vertical registration
# are preserved -- the female map stays a drop-in for the male one (F7-F9).
SLIM = [(13,0.74),(28,0.74),(42,0.78),(54,0.70),(68,0.72),(84,0.80),(102,0.84),
        (124,0.86),(145,0.88),(165,0.88),(190,0.86),(215,0.86),(274,0.89)]
BOOST= [(13,0.95),(45,0.93),(58,1.00),(82,1.02),(95,0.92),(110,0.86),(122,0.90),
        (132,1.02),(142,1.14),(152,1.22),(162,1.20),(172,1.10),(185,1.04),(205,1.00),(274,1.00)]
CORE_OUT, LIMB = 40.0, 56.0   # full boost below CORE_OUT, none above LIMB, smoothstep between
def interp(tbl, y):
    if y<=tbl[0][0]: return tbl[0][1]
    if y>=tbl[-1][0]: return tbl[-1][1]
    for (y0,s0),(y1,s1) in zip(tbl,tbl[1:]):
        if y0<=y<=y1:
            t=(y-y0)/(y1-y0); return s0+t*(s1-s0)
    return 1.0
def factor(dx, y):
    a=abs(dx)
    if a<=CORE_OUT: w=1.0
    elif a>=LIMB:   w=0.0
    else:
        t=(a-CORE_OUT)/(LIMB-CORE_OUT); w=1-(t*t*(3-2*t))   # smoothstep falloff
    return interp(SLIM,y)*(interp(BOOST,y)*w+1.0*(1-w))
def warp(z):
    ax=FRONT_AXIS if z.real<MIDX else BACK_AXIS
    dx=z.real-ax
    return complex(ax+dx*factor(dx,z.imag), z.imag)
def warp_seg(s):
    if isinstance(s,Line):           return Line(warp(s.start),warp(s.end))
    if isinstance(s,CubicBezier):    return CubicBezier(warp(s.start),warp(s.control1),warp(s.control2),warp(s.end))
    if isinstance(s,QuadraticBezier): return QuadraticBezier(warp(s.start),warp(s.control),warp(s.end))
    if isinstance(s,Arc):            return Arc(warp(s.start),s.radius,s.rotation,s.large_arc,s.sweep,warp(s.end))
    return s
def transform_d(d): return Path(*[warp_seg(seg) for seg in parse_path(d)]).d()

# --- stage 2: breasts replace the flat male pecs ----------------------------
# Egg/teardrop curve (fuller lower hemisphere), authored over each pectoral in
# the original coord space then carried through the same warp so it stays
# registered. chest1/chest2 keep their id/title/class -> selection engine intact.
K=0.5522847498
def breast(cx,cy,rx,rt,rb):
    return (f'M {cx:.2f},{cy-rt:.2f} '
            f'C {cx+rx*K:.2f},{cy-rt:.2f} {cx+rx:.2f},{cy-rt*K:.2f} {cx+rx:.2f},{cy:.2f} '
            f'C {cx+rx:.2f},{cy+rb*K:.2f} {cx+rx*K:.2f},{cy+rb:.2f} {cx:.2f},{cy+rb:.2f} '
            f'C {cx-rx*K:.2f},{cy+rb:.2f} {cx-rx:.2f},{cy+rb*K:.2f} {cx-rx:.2f},{cy:.2f} '
            f'C {cx-rx:.2f},{cy-rt*K:.2f} {cx-rx*K:.2f},{cy-rt:.2f} {cx:.2f},{cy-rt:.2f} Z')
BREASTS={'chest1':breast(104.5,81,13.5,10,15),   # figure's left pec
         'chest2': breast(72.5,81,13.5,10,15)}     # figure's right pec

# --- stage 3: line-art feminine hair ----------------------------------------
# The silhouette renders as thin double-traced bands (even-odd fill), so hair is
# drawn the same way: a centreline swept into a thin closed band. We drop the
# male hair subpaths of human_body and append feminine ones (all in original
# coords, so the warp carries them too).
import math
def band(pts, hw=0.75):
    n=len(pts); L=[]; R=[]
    for i in range(n):
        if i==0:        dx,dy=pts[1][0]-pts[0][0],   pts[1][1]-pts[0][1]
        elif i==n-1:    dx,dy=pts[-1][0]-pts[-2][0], pts[-1][1]-pts[-2][1]
        else:           dx,dy=pts[i+1][0]-pts[i-1][0], pts[i+1][1]-pts[i-1][1]
        d=math.hypot(dx,dy) or 1; nx,ny=-dy/d*hw, dx/d*hw
        L.append((pts[i][0]+nx,pts[i][1]+ny)); R.append((pts[i][0]-nx,pts[i][1]-ny))
    return 'M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in L+R[::-1])+' Z'
def mirror(pts,cx): return [(2*cx-x,y) for x,y in pts]
def female_hair(cx, top, jaw):
    outer=[(cx-9.5,jaw+9),(cx-13,top+38),(cx-15,top+24),(cx-13.5,top+9),(cx-7,top+0.5),
           (cx,top-0.5),(cx+7,top+0.5),(cx+13.5,top+9),(cx+15,top+24),(cx+13,top+38),(cx+9.5,jaw+9)]
    fore=[(cx-8.5,top+13),(cx-4,top+9.5),(cx,top+10.5),(cx+4,top+9.5),(cx+8.5,top+13)]
    part=[(cx,top+1),(cx-0.4,top+9)]
    return [band(outer,0.9),band(fore,0.7),band(part,0.5)]
def back_hair(cx, top, jaw):
    outer=[(cx-12,jaw-2),(cx-14,top+24),(cx-12,top+9),(cx-6,top+1),(cx,top),(cx+6,top+1),
           (cx+12,top+9),(cx+14,top+24),(cx+13,jaw+2),(cx+9,jaw+13),(cx,jaw+18),
           (cx-9,jaw+13),(cx-13,jaw+2),(cx-12,jaw-2)]
    strand=[(cx,top+4),(cx-0.5,jaw+12)]
    return [band(outer,0.95),band(strand,0.6)]
FRONT_HAIR=female_hair(88.5,14.5,54.0)
BACK_HAIR =back_hair(253.5,14.5,52.0)
DROP_SUB={44,45,46, 90,91,92,93}   # male hair subpaths (front, back) of human_body
def rebuild_human_body(d):
    subs=parse_path(d).continuous_subpaths()
    keep=[s.d() for i,s in enumerate(subs) if i not in DROP_SUB]
    return ' '.join(keep+FRONT_HAIR+BACK_HAIR)

# tolerant capture: matches both "/>" and ">" closings, any attribute order before d
el = re.compile(r'<path\b(.*?)\bd="([^"]*)"\s*/?>', re.DOTALL)
elements=[]
for m in el.finditer(src):
    attrs=' '.join(m.group(1).split())          # normalise whitespace, keep id/title/class
    idm=re.search(r'id="([^"]*)"',attrs); pid=idm.group(1) if idm else ''
    raw=m.group(2)
    if pid=='human_body': raw=rebuild_human_body(raw)
    elif pid in BREASTS:  raw=BREASTS[pid]
    elements.append((attrs, transform_d(raw)))

# bounds for viewBox
xs0=ys0=1e9; xs1=ys1=-1e9
for _,d in elements:
    x0,x1,y0,y1=parse_path(d).bbox()
    xs0=min(xs0,x0);xs1=max(xs1,x1);ys0=min(ys0,y0);ys1=max(ys1,y1)
pad=6; vb=f'{xs0-pad:.2f} {ys0-pad:.2f} {xs1-xs0+2*pad:.2f} {ys1-ys0+2*pad:.2f}'

lines=['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
       f'<svg version="1.1" id="svg1" xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:svg="http://www.w3.org/2000/svg" viewBox="{vb}">',
       '  <defs>',
       '    <style type="text/css" id="style1">.muscle{fill:#CCCCCC;fill-opacity:1;'
       'stroke:#ffffff;stroke-opacity:1;stroke-width:0.5;}</style>',
       '  </defs>',
       '  <g>']
for attrs,d in elements:                          # one <path> per line, self-closed -> valid XML + library-regex safe
    lines.append(f'    <path {attrs} d="{d}"/>')
lines.append('  </g>')
lines.append('</svg>')
out='\n'.join(lines)+'\n'
open('assets/maps/human_body_female.svg','w').write(out)
open('tracing/human_body_female.scaffold.svg','w').write(out)

print(f"wrote assets/maps/human_body_female.svg ({len(elements)} paths)")
print("        tracing/human_body_female.scaffold.svg")

# self-check
import xml.dom.minidom
xml.dom.minidom.parseString(out); print("XML: well-formed")
dart=re.compile(r'.* id="(.*)" title="(.*)" .* d="(.*)"')
print("library-regex lines:", sum(1 for ln in out.splitlines() if dart.search(ln)), "(expect 52)")
try:
    import cairosvg
    cairosvg.svg2png(url='assets/maps/human_body_female.svg',
                     write_to='tracing/_preview_female.png',
                     output_width=360, background_color='white')
    print("preview: tracing/_preview_female.png")
except ImportError:
    print("preview: skipped (pip install cairosvg to enable)")
