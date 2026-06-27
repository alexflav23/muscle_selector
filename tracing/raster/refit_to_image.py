import re, sys, numpy as np
from PIL import Image
from svgpathtools import parse_path, Path, Line, QuadraticBezier, CubicBezier, Arc
SP="/private/tmp/claude-501/-Users-flavian-projects-personal-muscle-selector/3041e061-dbc9-4989-b31a-0d0a788ab777/scratchpad"
REPO="/Users/flavian/projects/personal/muscle_selector"
NEW_IMG=sys.argv[1]
WRITE=len(sys.argv)>2 and sys.argv[2]=='write'
W,H=2304,1856; MIDX=1152.0

# target body bbox per figure from the new (lean) image
img=np.array(Image.open(NEW_IMG).convert('L')); body=img<235
cc=body.sum(axis=0); lo,hi=int(W*0.42),int(W*0.58); split=lo+int(np.argmin(cc[lo:hi]))
xall=np.where(body.any(axis=0))[0]
def ibbox(x0,x1):
    s=body[:,x0:x1]; ys=np.where(s.any(axis=1))[0]; xs=np.where(s.any(axis=0))[0]
    return x0+xs.min(),x0+xs.max(),ys.min(),ys.max()
TB={'front':ibbox(xall.min(),split),'back':ibbox(split,xall.max())}

# source body bbox per figure from current human_body silhouette (strip the anchor rect)
src=open(f'{REPO}/assets/maps/human_body_female.svg').read()
hb=re.search(r'id="human_body"[^>]*\bd="([^"]*)"',src).group(1)
hb=re.sub(r'^M 0,0 L 2304,0 L 2304,1856 L 0,1856 Z ','',hb)
P=parse_path(hb)
def sbbox(front):
    X0=1e9;X1=-1e9;Y0=1e9;Y1=-1e9
    for seg in P:
        zs=(seg.start,seg.control1,seg.control2,seg.end) if isinstance(seg,CubicBezier) else (seg.start,seg.end)
        for z in zs:
            if (z.real<MIDX)==front:
                X0=min(X0,z.real);X1=max(X1,z.real);Y0=min(Y0,z.imag);Y1=max(Y1,z.imag)
    return X0,X1,Y0,Y1
SB={'front':sbbox(True),'back':sbbox(False)}
print('SB',{k:tuple(round(v) for v in val) for k,val in SB.items()})
print('TB',{k:tuple(int(v) for v in val) for k,val in TB.items()})

def conform(z):
    f='front' if z.real<MIDX else 'back'
    sx0,sx1,sy0,sy1=SB[f]; ix0,ix1,iy0,iy1=TB[f]
    return complex(ix0+(z.real-sx0)/(sx1-sx0)*(ix1-ix0), iy0+(z.imag-sy0)/(sy1-sy0)*(iy1-iy0))
def ws(s):
    if isinstance(s,Line): return Line(conform(s.start),conform(s.end))
    if isinstance(s,CubicBezier): return CubicBezier(conform(s.start),conform(s.control1),conform(s.control2),conform(s.end))
    if isinstance(s,QuadraticBezier): return QuadraticBezier(conform(s.start),conform(s.control),conform(s.end))
    if isinstance(s,Arc): return Arc(conform(s.start),s.radius,s.rotation,s.large_arc,s.sweep,conform(s.end))
    return s
el=re.compile(r'(<path\b)(.*?)(\bd=")([^"]*)("\s*/?>)',re.DOTALL)
def repl(m):
    pid=re.search(r'id="([^"]*)"',m.group(2)).group(1)
    if pid=='human_body': return m.group(0)
    return m.group(1)+m.group(2)+m.group(3)+Path(*[ws(s) for s in parse_path(m.group(4))]).d()+m.group(5)
out=el.sub(repl,src)
if WRITE:
    open(f'{REPO}/assets/maps/human_body_female.svg','w').write(out)
    Image.open(NEW_IMG).convert('RGB').save(f'{REPO}/assets/maps/human_body_female.png')
    print('WROTE refit svg + new png')
else:
    open(SP+'/refit_female.svg','w').write(out)
    print('preview refit_female.svg')
