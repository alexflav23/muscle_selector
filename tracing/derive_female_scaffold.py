"""
Derive the female muscle-map scaffold from the male map by an anatomical
proportional warp (narrow shoulders -> pinched waist -> wide hips/pelvis,
applied about each figure's vertical axis). Only x is moved as a function of y,
so every id/title/class and all vertical registration are preserved.

Run from the repo root:  python tracing/derive_female_scaffold.py
Needs: pip install svgpathtools cairosvg
Writes: assets/maps/human_body_female.svg  +  tracing/human_body_female.scaffold.svg
"""
import re
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc

src = open('assets/maps/human_body.svg').read()
FRONT_AXIS, BACK_AXIS, MIDX = 88.5, 254.0, 171.6
PROFILE = [(0,0.95),(45,0.90),(58,0.82),(72,0.83),(88,0.90),(104,0.90),
           (118,0.83),(130,0.95),(142,1.13),(158,1.12),(175,1.04),(192,1.00),(280,0.99)]
def s_of_y(y):
    if y<=PROFILE[0][0]: return PROFILE[0][1]
    if y>=PROFILE[-1][0]: return PROFILE[-1][1]
    for (y0,s0),(y1,s1) in zip(PROFILE,PROFILE[1:]):
        if y0<=y<=y1:
            t=(y-y0)/(y1-y0); return s0+t*(s1-s0)
    return 1.0
def warp(z):
    ax=FRONT_AXIS if z.real<MIDX else BACK_AXIS
    return complex(ax+(z.real-ax)*s_of_y(z.imag), z.imag)
def warp_seg(s):
    if isinstance(s,Line):           return Line(warp(s.start),warp(s.end))
    if isinstance(s,CubicBezier):    return CubicBezier(warp(s.start),warp(s.control1),warp(s.control2),warp(s.end))
    if isinstance(s,QuadraticBezier): return QuadraticBezier(warp(s.start),warp(s.control),warp(s.end))
    if isinstance(s,Arc):            return Arc(warp(s.start),s.radius,s.rotation,s.large_arc,s.sweep,warp(s.end))
    return s
def transform_d(d): return Path(*[warp_seg(seg) for seg in parse_path(d)]).d()

# tolerant capture: matches both "/>" and ">" closings, any attribute order before d
el = re.compile(r'<path\b(.*?)\bd="([^"]*)"\s*/?>', re.DOTALL)
elements=[]
for m in el.finditer(src):
    attrs=' '.join(m.group(1).split())          # normalise whitespace, keep id/title/class
    elements.append((attrs, transform_d(m.group(2))))

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
