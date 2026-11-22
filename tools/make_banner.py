"""Render the profile banner: Michelangelo's Creation of Adam as coloured ASCII,
with the name built out of glyphs inside the same character grid.

    python tools/make_banner.py      # writes banner.png (needs pillow, numpy; macOS Menlo font)
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
SRC=os.path.join(ROOT,'assets','creation-of-adam.png'); OUT=os.path.join(ROOT,'banner.png')
# same framing as the MacBook wallpaper: the whole painting, plus generated
# plaster grain above and below (2880x1864 screen aspect, scaled to 2400 wide)
box=(88,10,2488,1088); W,FH=2400,round(2400*1864/2880); fs=8
H=round(W*(box[3]-box[1])/(box[2]-box[0]))  # height of the painting band
NAME='KRABDUKE'; TAGLINE='building things to see how they work'
BONE=np.array([241,231,210]); GOLD=np.array([201,165,107])
FONT='/System/Library/Fonts/Menlo.ttc'
font=ImageFont.truetype(FONT,fs,index=1)  # Menlo Bold
cw=font.getlength('M'); ch=fs*0.98
cols,rows=int(W/cw),int(H/ch)
ramp=" .:;i1tfLCG08@"
rgb=Image.open(SRC).convert('RGB').crop(box)
hsv=np.asarray(rgb.convert('HSV'),float)/255
L=np.asarray(rgb.convert('L'),float)/255
hue,sat=hsv[...,0],hsv[...,1]
def sm(e0,e1,x): x=np.clip((x-e0)/(e1-e0),0,1); return x*x*(3-2*x)
sat_m=np.asarray(Image.fromarray((sat*255).astype('uint8')).filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.GaussianBlur(3)),float)/255
blue=sm(0.08,0.02,np.abs(hue-0.6))*sm(0.12,0.25,sat_m)
mask=sm(0.088,0.125,sat_m)*(1-blue)
hw,hh=rgb.size
m=Image.fromarray((mask*255).astype('uint8')).resize((hw//2,hh//2))
m=m.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.5)).resize((hw,hh),Image.BICUBIC)
mask=np.asarray(m,float)/255
# hand-traced region: God's white robe + grey hair/beard (low saturation, same as wall)
poly=[(1395,150),(1500,110),(1660,120),(1850,170),(2030,250),(2150,380),(2160,520),(2080,640),(1930,700),(1760,690),(1600,620),(1480,520),(1420,420),(1380,290)]
pm=Image.new('L',(hw,hh),0); ImageDraw.Draw(pm).polygon([(x-box[0],y-box[1]) for x,y in poly],fill=255)
ImageDraw.Draw(pm).ellipse((500-box[0],790-box[1],740-box[0],895-box[1]),fill=255)  # pale patch on Adam's thigh
pm=np.asarray(pm.filter(ImageFilter.GaussianBlur(10)),float)/255
mask=np.maximum(mask,pm)
def cell(a): return np.asarray(Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).resize((cols,rows),Image.BOX),float)/255
Lc=cell(L)
def blur(a,r): return np.asarray(Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(r)),float)/255
Lc=np.clip(Lc+1.6*(Lc-blur(Lc,max(cols,rows)/40)),0,1)
Mc=cell(mask)
lo,hi=np.percentile(Lc[Mc>0.5],[2,99.5]); v=np.clip((Lc-lo)/(hi-lo),0,1)**1.25
v=v*(0.04+0.96*Mc**1.4)
xx=np.linspace(0,1,cols)[None,:]; v=v*sm(0.0,0.012,xx)*sm(1.0,0.988,xx)
yy=np.linspace(0,1,rows)[:,None]; v=v*sm(1.0,0.96,yy)  # soften the bottom edge
# limited palette from the painting's own colours (cell-level k-means)
C=np.asarray(rgb.resize((cols,rows),Image.BOX),float)
X=C.reshape(-1,3); wts=Mc.reshape(-1)
rng=np.random.default_rng(0); K=8
cent=X[rng.choice(len(X),K,p=wts/wts.sum(),replace=False)]
for _ in range(25):
    lab=((X[:,None,:]-cent[None])**2).sum(-1).argmin(1)
    for k in range(K):
        sel=lab==k
        if (wts[sel]).sum()>0: cent[k]=(X[sel]*wts[sel,None]).sum(0)/wts[sel].sum()
# normalise palette to full brightness, gentle saturation boost
pal=[]
for c in cent:
    m=c.mean(); c=m+(c-m)*1.7; c=np.clip(c,0,None); pal.append(c/max(c.max(),1)*255)
pal=np.array(pal); lab=lab.reshape(rows,cols)
# --- generated margins: extend the plaster 'dust' above and below ---
ch_rows=int(FH/ch); off=(ch_rows-rows)//2
V=np.zeros((ch_rows,cols)); LAB=np.zeros((ch_rows,cols),int)
V[off:off+rows]=v; LAB[off:off+rows]=lab
wall_lab=np.bincount(lab[v<0.08].ravel()).argmax()
rng2=np.random.default_rng(7)
noise=blur(rng2.random((ch_rows,cols)),3); noise=(noise-noise.min())/(noise.max()-noise.min())
ry=np.arange(ch_rows)[:,None]
d_out=np.where(ry<off,off-ry,np.where(ry>=off+rows,ry-(off+rows)+1,0))
fade=np.exp(-d_out/(ch_rows*0.12))*(d_out>0)
spark=(rng2.random((ch_rows,cols))<0.10*noise**1.5)*(0.045+0.04*rng2.random((ch_rows,cols)))
v=np.where(d_out>0,spark*fade,V); lab=np.where(d_out>0,wall_lab,LAB); rows,H=ch_rows,FH
def cellg(a): return np.asarray(Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).resize((cols,rows),Image.BOX),float)/255
# --- name built from glyphs inside the grid, centred in the top margin ---
top=off*ch  # pixel height of the top margin
nf=ImageFont.truetype(FONT,int(top*0.56),index=1)
tf=ImageFont.truetype(FONT,int(top*0.11),index=0)
nm_img=Image.new('L',(W,H),0); nd=ImageDraw.Draw(nm_img)
b0=nd.textbbox((0,0),NAME,font=nf); t0=nd.textbbox((0,0),TAGLINE,font=tf)
gap=int(top*0.07); blockh=(b0[3]-b0[1])+gap+(t0[3]-t0[1])
nx=(W-(b0[2]-b0[0]))//2-b0[0]; ny=int((top-blockh)/2)-b0[1]
nd.text((nx,ny),NAME,font=nf,fill=255); nb=nd.textbbox((nx,ny),NAME,font=nf)
tx=(W-(t0[2]-t0[0]))//2-t0[0]; ty=nb[3]+gap-t0[1]
nm=cellg(np.asarray(nm_img,float)/255)
tb=nd.textbbox((tx,ty),TAGLINE,font=tf)
zone=np.zeros_like(nm); zone[max(0,int(nb[1]/ch)-2):int(tb[3]/ch)+3, max(0,int(min(nb[0],tb[0])/cw)-4):min(cols,int(max(nb[2],tb[2])/cw)+5)]=1
v=v*(1-np.clip(blur(zone,3)*1.6,0,1))
over={}
for y in range(rows):
    for x in range(cols):
        cv=nm[y,x]
        if cv>0.10: over[(y,x)]=(ramp[min(len(ramp)-1,int(cv*(len(ramp)-1)+0.5))], tuple(int(q) for q in BONE*(0.45+0.55*cv)))
img=Image.new('RGB',(W,H),(8,8,12)); d=ImageDraw.Draw(img)
ox=(W-cols*cw)/2; oy=(H-rows*ch)/2; lines=[]
for y in range(rows):
    s=''
    for x in range(cols):
        if (y,x) in over:
            c,col=over[(y,x)]; s+=c; d.text((ox+x*cw,oy+y*ch),c,fill=col,font=font); continue
        val=v[y,x]; c=ramp[min(len(ramp)-1,int(val*(len(ramp)-1)+0.5))]; s+=c
        if c!=' ': d.text((ox+x*cw,oy+y*ch),c,fill=tuple(int(q) for q in pal[lab[y,x]]*(0.28+0.72*val**0.7)),font=font)
    lines.append(s.rstrip())
d.text((tx,ty),TAGLINE,font=tf,fill=tuple(int(q) for q in GOLD))
img.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save(OUT,optimize=True)
print(OUT,cols,'x',rows)
