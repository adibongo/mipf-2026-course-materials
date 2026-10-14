import sys, os
from PIL import Image, ImageDraw, ImageFont
out=sys.argv[1]
P=lambda s:[tuple(map(float,p.split(','))) for p in s.split()]
facets=[("512,25.6 90.77,268.8 212.92,339.33 512,166.66","#D99A2B"),
 ("90.77,268.8 90.77,755.2 212.92,684.67 212.92,339.33","#1C7293"),
 ("90.77,755.2 512,998.4 512,857.34 212.92,684.67","#0B5E82"),
 ("512,998.4 933.23,755.2 811.08,684.67 512,857.34","#1F2A66"),
 ("933.23,755.2 933.23,268.8 811.08,339.33 811.08,684.67","#0B5E82"),
 ("933.23,268.8 512,25.6 512,166.66 811.08,339.33","#141B4D")]
inner="512,166.66 212.92,339.33 212.92,684.67 512,857.34 811.08,684.67 811.08,339.33"
outer="512,25.6 90.77,268.8 90.77,755.2 512,998.4 933.23,755.2 933.23,268.8"
def svg(path, mono=False, text="MIPF"):
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">']
    s.append('<path d="M %s Z" fill="#FFFFFF"/>' % inner.replace(' ',' L '))
    for pts,c in facets:
        s.append('<path d="M %s Z" fill="%s"/>' % (pts.replace(' ',' L '), "#141B4D" if mono else c))
    for pts in (outer,inner):
        s.append('<path d="M %s Z" fill="none" stroke="#141B4D" stroke-width="3" stroke-linejoin="round"/>' % pts.replace(' ',' L '))
    s.append('<text x="512" y="578" text-anchor="middle" fill="#141B4D" font-family="Lato, Inter, Helvetica, Arial, sans-serif" font-weight="800" font-size="196" letter-spacing="-6">%s</text></svg>' % text)
    open(path,"w").write("\n".join(s))
def png(path, size=1024, mono=False, text="MIPF"):
    k=size/1024; im=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(im)
    sc=lambda pts:[(x*k,y*k) for x,y in P(pts.replace(',',',').replace(' ',' '))]
    d.polygon(sc(inner),fill="#FFFFFF")
    for pts,c in facets: d.polygon(sc(pts),fill="#141B4D" if mono else c)
    for pts in (outer,inner): d.line(sc(pts)+[sc(pts)[0]],fill="#141B4D",width=max(1,int(3*k)),joint="curve")
    f=None
    for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf","/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(fp): f=ImageFont.truetype(fp,int(190*k)); break
    w=d.textlength(text,font=f); d.text((512*k-w/2,578*k),text,font=f,fill="#141B4D",anchor="ls")
    im.save(path)
svg(out+"/mipf_hex.svg"); svg(out+"/mipf_hex_mono.svg",mono=True)
png(out+"/mipf_hex.png",1024); png(out+"/mipf_hex_256.png",256); png(out+"/mipf_hex_mono.png",512,mono=True)
