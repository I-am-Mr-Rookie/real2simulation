
import json,re,io,subprocess,sys
from PIL import Image, ImageDraw
W=r'C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S25e-orch208'
o=json.load(open(W+'/Run-System/Runs/S25e-orch208/scan.json'))
sel=[p for p in o['images'] if not re.search(r'^(Build/web/public|evidence/brand|evidence/clips)/',p)]
print(len(sel))
# read blob bytes from the scanned commit (covers deleted-in-HEAD paths too)
objs={}
for l in subprocess.run(['git','rev-list','--objects','1b9ab540'],capture_output=True,cwd=W).stdout.decode('utf8','replace').splitlines():
    s,_,p=l.partition(' ')
    if p in sel: objs.setdefault(p,s)
T=220; per=48
for k in range(0,len(sel),per):
    chunk=sel[k:k+per]; cols=8; rows=(len(chunk)+cols-1)//cols
    sheet=Image.new('RGB',(cols*T,rows*(T+14)),'white'); d=ImageDraw.Draw(sheet)
    for i,p in enumerate(chunk):
        b=subprocess.run(['git','cat-file','blob',objs[p]],capture_output=True,cwd=W).stdout
        try:
            im=Image.open(io.BytesIO(b)).convert('RGB'); im.thumbnail((T,T))
            sheet.paste(im,((i%cols)*T,(i//cols)*(T+14)+14))
        except Exception as e: pass
        d.text(((i%cols)*T+2,(i//cols)*(T+14)),str(k+i)+' '+p.split('/')[-1][:30],fill='red')
    sheet.save(W+f'/Run-System/Runs/S25e-orch208/ui-sheet-{k//per}.jpg',quality=70)
json.dump(sel,open(W+'/Run-System/Runs/S25e-orch208/ui-sheet-index.json','w'),indent=0)

