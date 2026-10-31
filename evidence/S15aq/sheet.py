import glob,sys
from PIL import Image, ImageChops
d=sys.argv[1]
a=Image.open(d+'/1280-no-preference-00.png').convert('RGB'); b=Image.open(d+'/1280-reduce-00.png').convert('RGB')
print('rest diff bbox 1280 motion vs reduce @0:', ImageChops.difference(a,b).getbbox())
for tag,w in [('1280-no-preference',1280),('390-no-preference',390),('1280-reduce',1280)]:
    fs=sorted(glob.glob(d+'/'+tag+'-*.png')); ims=[Image.open(f).convert('RGB') for f in fs]
    s=0.25 if w==1280 else 0.5
    ims=[i.resize((int(i.width*s),int(i.height*s))) for i in ims]
    W=sum(i.width for i in ims)+4*len(ims); H=max(i.height for i in ims)
    sh=Image.new('RGB',(W,H),'white'); x=0
    for i in ims: sh.paste(i,(x,0)); x+=i.width+4
    sh.save(d+'/../sheet-'+tag+'.png'); print(tag,len(fs))

