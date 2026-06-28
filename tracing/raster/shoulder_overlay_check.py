import re, sys, json, cairosvg
from PIL import Image
from svgpathtools import parse_path, Path, Line, CubicBezier, QuadraticBezier, Arc
SP="/private/tmp/claude-501/-Users-flavian-projects-personal-muscle-selector/3041e061-dbc9-4989-b31a-0d0a788ab777/scratchpad"
REPO="/Users/flavian/projects/personal/muscle_selector"
# SVG(2304x1856) -> app screenshot(1170x2532), calibrated transform (same layout)
SX,OX,OY=0.4992,13.9,552.1
GENDER=sys.argv[1]; BASE=sys.argv[2]   # base app screenshot (body visible)
# per-figure translate: {"front":[dx,dy],"back":[dx,dy]}  (front=shoulder1/2, back=shoulder3/4)
T=json.loads(sys.argv[3])
SVG=f'{REPO}/assets/maps/'+('human_body_female.svg' if GENDER=='female' else 'human_body.svg')
src=open(SVG).read()
paths={re.search(r'id="([^"]*)"',a).group(1):d for a,d in re.findall(r'<path ([^>]*?)d="([^"]*)"\s*/>',src)}
def shift(P,dx,dy):
    f=lambda z: complex(z.real+dx,z.imag+dy)
    def ws(s):
        if isinstance(s,Line): return Line(f(s.start),f(s.end))
        if isinstance(s,CubicBezier): return CubicBezier(f(s.start),f(s.control1),f(s.control2),f(s.end))
        if isinstance(s,QuadraticBezier): return QuadraticBezier(f(s.start),f(s.control),f(s.end))
        if isinstance(s,Arc): return Arc(f(s.start),s.radius,s.rotation,s.large_arc,s.sweep,f(s.end))
        return s
    return Path(*[ws(s) for s in P]).d()
# T = {fdx,fdy,bdx,bdy}: symmetric OUTWARD shift (sh1/sh3 left=-, sh2/sh4 right=+)
per={'shoulder1':(-T['fdx'],T['fdy']),'shoulder2':(T['fdx'],T['fdy']),
     'shoulder3':(-T['bdx'],T['bdy']),'shoulder4':(T['bdx'],T['bdy'])}
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1170" height="2532" viewBox="0 0 1170 2532">',
     f'<g transform="translate({OX},{OY}) scale({SX})">']
for sid,(dx,dy) in per.items():
    d2=shift(parse_path(paths[sid]),dx,dy)
    svg.append(f'<path d="{d2}" fill="#ff1744" fill-opacity="0.5" stroke="#b71c1c" stroke-width="3"/>')
svg+=['</g>','</svg>']
open(SP+'/_sh.svg','w').write('\n'.join(svg))
cairosvg.svg2png(url=SP+'/_sh.svg',write_to=SP+'/_sh.png',output_width=1170,output_height=2532,background_color='rgba(0,0,0,0)')
out=Image.alpha_composite(Image.open(BASE).convert('RGBA'),Image.open(SP+'/_sh.png').convert('RGBA')).convert('RGB')
out.crop((40,820,1140,1180)).resize((733,240)).save(SP+'/shoulder_check.png')
print('shoulder_check.png  T=',T)
