import re, sys, json, cairosvg
from PIL import Image
SP="/private/tmp/claude-501/-Users-flavian-projects-personal-muscle-selector/3041e061-dbc9-4989-b31a-0d0a788ab777/scratchpad"
# transform SVG(2304x1856) -> app screenshot(1170x2532), calibrated from rendered calves:
# app_x = 0.641*svg_x - 224.4 ; app_y = 0.641*svg_y + 682
SX,OX,SY,OY=0.4992,13.9,0.4992,552.1
P=json.loads(sys.argv[1])
def calf(cx,ytop,w,h):
    ymid=ytop+h*0.34; ybot=ytop+h
    return (f'M {cx},{ytop} C {cx+w*0.72},{ytop} {cx+w},{ymid-h*0.14} {cx+w},{ymid} '
            f'C {cx+w},{ymid+h*0.22} {cx+w*0.42},{ybot} {cx},{ybot} '
            f'C {cx-w*0.42},{ybot} {cx-w},{ymid+h*0.22} {cx-w},{ymid} '
            f'C {cx-w},{ymid-h*0.14} {cx-w*0.72},{ytop} {cx},{ytop} Z')
Lx,Rx,sep,ytop,h,wo,wi,drop=(P[k] for k in ['Lx','Rx','sep','ytop','h','wo','wi','drop'])
shapes=[calf(Lx-sep,ytop,wo,h-12),calf(Lx+sep,ytop+drop,wi,h),
        calf(Rx+sep,ytop,wo,h-12),calf(Rx-sep,ytop+drop,wi,h)]
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1170" height="2532" viewBox="0 0 1170 2532">',
     f'<g transform="translate({OX},{OY}) scale({SX})">']
for d in shapes: svg.append(f'<path d="{d}" fill="#ff1744" fill-opacity="0.55" stroke="#b71c1c" stroke-width="3"/>')
svg+=['</g>','</svg>']
open(SP+'/_app.svg','w').write('\n'.join(svg))
cairosvg.svg2png(url=SP+'/_app.svg',write_to=SP+'/_app.png',output_width=1170,output_height=2532,background_color='rgba(0,0,0,0)')
base=Image.open(SP+'/male_calves_clean.png').convert('RGBA')
out=Image.alpha_composite(base,Image.open(SP+'/_app.png').convert('RGBA')).convert('RGB')
w,hh=out.size
out.crop((int(w*0.50),int(hh*0.42),w,int(hh*0.66))).resize((640,460)).save(SP+'/appcheck.png')
print('candidate over REAL app -> appcheck.png (red=candidate, ignore old blue)')
