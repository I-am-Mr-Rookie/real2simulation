import subprocess,re,json,sys,collections,hashlib,os
R=os.getcwd()
def g(*a):return subprocess.run(['git',*a],capture_output=True,cwd=R).stdout
# blob -> (first commit, path)
bm={};
cur=None
for l in g('log','--all','--raw','--no-abbrev','--format=C:%H').decode('utf8','replace').splitlines():
    if l.startswith('C:'):cur=l[2:]
    elif l.startswith(':'):
        m,p=l.split('\t',1)[0].split(),l.split('\t',1)[1:]
        for b in (m[2],m[3]):
            if set(b)!={'0'}:bm.setdefault(b,(cur,p[-1] if p else '?'))
tracked={}
for l in g('ls-tree','-r','--full-tree','HEAD').decode('utf8','replace').splitlines():
    a,p=l.split('\t',1);tracked[a.split()[2]]=p
# env values (in-process only)
envn={}
ep='C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.env'
if not os.path.exists(ep):
    ep=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(R)))) if False else R,'.env')
for l in open(ep,encoding='utf8',errors='replace') if os.path.exists(ep) else []:
    l=l.strip()
    if '=' in l and not l.startswith('#'):
        k,v=l.split('=',1);v=v.strip().strip('"\'')
        if len(v)>=8:envn[k.strip()]=v.encode()
RULES={'aws_akia':r'\b(AKIA|ASIA)[0-9A-Z]{16}\b','aws_secret':r'(?i)aws_secret_access_key\W{0,4}[A-Za-z0-9/+=]{40}\b','hf':r'\bhf_[A-Za-z0-9]{30,}','openai':r'\bsk-(proj-)?[A-Za-z0-9_-]{32,}','anthropic':r'\bsk-ant-[A-Za-z0-9_-]{20,}','gh':r'\b(ghp_|gho_|ghs_|github_pat_)[A-Za-z0-9_]{30,}','clerk':r'\b(sk|pk)_(live|test)_[A-Za-z0-9]{20,}','modal':r'\b(ak|as)-[A-Za-z0-9]{20,}\b','privkey':r'-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----','jwt':r'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}','slack':r'\bxox[baprs]-[A-Za-z0-9-]{20,}','meta_llama':r'\b(LLM|LLAMA|META)[A-Z_]*(KEY|TOKEN)\s*[=:]\s*\S{16,}','envkv':r'(?m)^\s*(export\s+)?[A-Z][A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)\s*=\s*[\'"]?[A-Za-z0-9_\-/+=.]{20,}','baseten':r'(?i)baseten\W{0,20}[A-Za-z0-9]{8}\.[A-Za-z0-9]{32}','railway':r'(?i)railway[_a-z]*token\W{0,5}[0-9a-f-]{36}','modal_tok':r'(?i)modal_token_(id|secret)\s*[=:]\s*\S{12,}'}
RX={k:re.compile(v) for k,v in RULES.items()}
find=[];n=0;skipped=0
p=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,cwd=R)
import threading
def feed():
    for b in bm:p.stdin.write((b+'\n').encode())
    p.stdin.close()
threading.Thread(target=feed).start()
while True:
    h=p.stdout.readline()
    if not h:break
    s=h.split()
    if len(s)<3:continue
    sha,t,sz=s[0].decode(),s[1],int(s[2]);d=p.stdout.read(sz);p.stdout.read(1)
    n+=1
    if t!=b'blob':continue
    if sz>8_000_000 or b'\0' in d[:8000]:skipped+=1;continue
    c,path=bm[sha];tx=d.decode('utf8','replace')
    for k,rx in RX.items():
        for m in rx.finditer(tx):
            find.append(dict(rule=k,path=path,commit=c[:8],tracked=sha in tracked,mask=m.group(0)[:4]+'...',line=tx.count('\n',0,m.start())+1));break
    for k,v in envn.items():
        if v in d:find.append(dict(rule='ENV_VALUE_MATCH',name=k,path=path,commit=c[:8],tracked=sha in tracked))
pat=re.compile(r'(^|/)(\.env($|\.)|\.playwright-mcp/|\.tmp-|archive/06 Real User data|.*storage[-_]?state.*|.*cookies?.*\.(json|txt|sqlite)$|.*\.(pem|key|p12|pfx)$|.*Updated_Instructions.*\.pdf$|.*\.(mp4|mov|mkv|webm)$)',re.I)
pf=collections.defaultdict(set)
for b,(c,pth) in bm.items():
    if pat.search(pth):pf[pth].add(c[:8])
big=[(p_,)for p_ in []]
out=dict(commits=len(g('rev-list','--all').split()),blobs=n,skipped=skipped,tracked_files=len(tracked),env_names=len(envn),findings=find,pathflags={k:sorted(v)[:2] for k,v in pf.items()},tracked_pathflags=[p_ for p_ in tracked.values() if pat.search(p_)])
json.dump(out,open('Run-System/Runs/S25c-orch155/scan.json','w'),indent=1)
cnt=collections.Counter((f['rule'],f['tracked']) for f in find)
print(out['commits'],n,skipped,len(tracked),len(envn),dict(cnt),len(pf),len(out['tracked_pathflags']))

