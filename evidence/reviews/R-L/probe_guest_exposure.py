
import json,sys,re,hashlib
sys.path.insert(0,'.')
from Build.library.guest import load_guest
m,objs=load_guest()
a=json.load(open('evidence/S10/acceptance/acceptance.json'))
c0=a['cases'][0]
rep=c0['replay']; print('replay keys',list(rep.keys()))
mt=json.dumps(m)
print('manifest bytes',len(mt))
for d in m['demos']:
    art=d.get('artifact') or {}
    print(d['id'],d.get('label'),d.get('availability'),art.get('kind'),art.get('bytes'),(d.get('reason') or '')[:60])
secrets={str(v) for v in rep.values() if isinstance(v,str)}
blob=mt+''.join(o.decode() for o in objs.values())
print('replay hash leak',[s for s in secrets if s in blob])
print('acceptance sha served?', hashlib.sha256(open('evidence/S10/acceptance/acceptance.json','rb').read()).hexdigest() in objs)
for sha,o in objs.items():
    t=o.decode(); j=json.loads(t)
    keys=set()
    def walk(x,p=''):
        if isinstance(x,dict):
            for k,v in x.items(): keys.add(k); walk(v)
        elif isinstance(x,list):
            for v in x[:3]: walk(v)
    walk(j)
    print(sha[:10],len(o),sorted(k for k in keys if re.search('grav|seed|g$|answer|replay|hash|sha',k)), 'has9.81' if '9.81' in t else '', 'seed42' if re.search(r'"seed": ?42',t) else '')
print('mf 9.81', '9.81' in mt, 'seed' in mt, 'gravity' in mt)

