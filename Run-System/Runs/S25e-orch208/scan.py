"""S25e pre-publication scan of every object reachable from main (what a push of main publishes).
Reuses S25c-orch155 scan.py rules; adds email/phone, >50 MB, private-path and media checks. Prints no secret values."""
import subprocess, re, json, sys, collections, os
REF = sys.argv[1] if len(sys.argv) > 1 else 'main'
ROOT = 'C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon'
def g(*a): return subprocess.run(['git', *a], capture_output=True, cwd=ROOT).stdout
first = {}  # blob -> (first commit seen, path)
cur = None
for l in g('log', REF, '--raw', '--no-abbrev', '--no-renames', '--format=C:%H').decode('utf8', 'replace').splitlines():
    if l.startswith('C:'): cur = l[2:]
    elif l.startswith(':'):
        meta, path = l.split('\t', 1)
        b = meta.split()[3]
        if set(b) != {'0'}: first[b] = (cur, path)  # log is newest-first, so last write = oldest commit
objs = {}
for l in g('rev-list', '--objects', REF).decode('utf8', 'replace').splitlines():
    s, _, p = l.partition(' ')
    objs[s] = p
env = {}
ep = os.path.join(ROOT, '.env')
for l in (open(ep, encoding='utf8', errors='replace') if os.path.exists(ep) else []):
    l = l.strip()
    if '=' in l and not l.startswith('#'):
        k, v = l.split('=', 1); v = v.strip().strip('"\'')
        if len(v) >= 8: env[k.strip()] = v.encode()
RULES = {'aws_akia': r'\b(AKIA|ASIA)[0-9A-Z]{16}\b', 'aws_secret': r'(?i)aws_secret_access_key\W{0,4}[A-Za-z0-9/+=]{40}\b', 'hf': r'\bhf_[A-Za-z0-9]{30,}', 'openai': r'\bsk-(proj-)?[A-Za-z0-9_-]{32,}', 'anthropic': r'\bsk-ant-[A-Za-z0-9_-]{20,}', 'gh': r'\b(ghp_|gho_|ghs_|ghu_|github_pat_)[A-Za-z0-9_]{30,}', 'clerk': r'\b(sk|pk)_(live|test)_[A-Za-z0-9]{20,}', 'modal': r'\b(ak|as)-[A-Za-z0-9]{20,}\b', 'privkey': r'-----BEGIN (RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY-----', 'jwt': r'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', 'slack': r'\bxox[baprs]-[A-Za-z0-9-]{20,}', 'meta_llama': r'\b(LLM|LLAMA|META)[A-Z_]*(KEY|TOKEN)[ \t]*[=:][ \t]*\S{16,}', 'envkv': r'(?m)^[ \t]*(export[ \t]+)?[A-Z][A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)[ \t]*=[ \t]*[\'"]?[A-Za-z0-9_\-/+=.]{20,}', 'baseten': r'(?i)baseten\W{0,20}[A-Za-z0-9]{8}\.[A-Za-z0-9]{32}', 'railway': r'(?i)railway[_a-z]*token\W{0,5}[0-9a-f-]{36}', 'modal_tok': r'(?i)modal_token_(id|secret)[ \t]*[=:][ \t]*\S{12,}', 'conn_str': r'\b(postgres(ql)?|mysql|mongodb(\+srv)?|redis|amqp)://[^\s:@/]+:[^\s@/]{6,}@', 'google_api': r'\bAIza[0-9A-Za-z_-]{35}\b', 'stripe': r'\b(rk|sk)_live_[0-9A-Za-z]{20,}'}
RX = {k: re.compile(v) for k, v in RULES.items()}
EMAIL = re.compile(rb'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE = re.compile(rb'(\+?880[- ]?1[3-9]\d{8}\b|(?<![\d.])01[3-9]\d{8}(?![\d.]))')
sec, envhits, big, skipped = [], [], [], 0
emails = collections.defaultdict(set); phones = collections.defaultdict(set)
blobs = [s for s in objs if objs[s]]
p = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=ROOT)
import threading
def feed():
    for b in blobs: p.stdin.write((b + '\n').encode())
    p.stdin.close()
threading.Thread(target=feed).start()
nblob = 0
while True:
    h = p.stdout.readline()
    if not h: break
    s = h.split()
    if len(s) < 3: continue
    sha, t, sz = s[0].decode(), s[1], int(s[2]); d = p.stdout.read(sz); p.stdout.read(1)
    if t != b'blob': continue
    nblob += 1
    c, path = first.get(sha, ('?', objs[sha]))
    if sz > 50_000_000: big.append(dict(path=path, commit=c[:8], bytes=sz))
    for k, v in env.items():
        if v in d: envhits.append(dict(name=k, path=path, commit=c[:8]))
    if sz > 8_000_000 or b'\0' in d[:8000]: skipped += 1; continue
    tx = d.decode('utf8', 'replace')
    for k, rx in RX.items():
        m = rx.search(tx)
        if m: sec.append(dict(rule=k, path=path, commit=c[:8], line=tx.count('\n', 0, m.start()) + 1, mask=m.group(0)[:4] + '...'))
    for m in EMAIL.finditer(d): emails[m.group(0).decode().lower()].add(path)
    for m in PHONE.finditer(d): phones[m.group(0).decode()[-4:]].add(path)
PATHRX = re.compile(r'(^|/)(\.env($|\.)|archive/|Videos for Meta AI Hackathon|logo-sketches|\.playwright-mcp/|\.tmp-|storage[-_]?state|cookies?\.(json|txt|sqlite)$|\.(pem|key|p12|pfx)$|Updated_Instructions.*\.pdf$|Build Notes\.pdf|Hackathon Credit Terms\.pdf|test-data/private/|uploads/)', re.I)
MEDIA = re.compile(r'\.(mp4|mov|mkv|webm|avi|m4v|gif)$', re.I)
IMG = re.compile(r'\.(png|jpe?g|webp|bmp|tiff?|ico|avif)$', re.I)
paths = sorted({pp for pp in objs.values() if pp})
out = dict(ref=REF, head=g('rev-parse', REF).decode().strip(), commits=len(g('rev-list', REF).split()), objects=len(objs), blobs=nblob, text_skipped=skipped, paths=len(paths),
    env_names_checked=len(env), secret_hits=sec, env_value_hits=envhits, over_50mb=big,
    emails={e: sorted(v)[:5] + ([f'+{len(v)-5} more'] if len(v) > 5 else []) for e, v in emails.items()},
    phones_last4={k: sorted(v)[:5] for k, v in phones.items()},
    private_paths=[pp for pp in paths if PATHRX.search(pp)], media=[pp for pp in paths if MEDIA.search(pp)],
    images=[pp for pp in paths if IMG.search(pp)])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scan.json'), 'w'), indent=1)
print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in out.items()}))

