"""N03 loopback check: real uvicorn + storage router; Node fetch streams multipart (duplex half, chunked) like the BFF.
Synthetic bytes, temp data dir, 127.0.0.1 only. Run from repo root: python -m evidence.N03.loopback_check
"""
import os, subprocess, sys, tempfile, threading, time
import uvicorn
from fastapi import FastAPI
from Build.api.storage import Store, create_router

os.environ["WORKSPACE_INTERNAL_TOKEN"] = "synthetic-loopback-token"
app = FastAPI()
app.include_router(create_router(Store(tempfile.mkdtemp()), probe=lambda p: 3.0))
server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8763, log_level="warning"))
threading.Thread(target=server.run, daemon=True).start()
time.sleep(1.5)
JS = r"""
const H = { 'x-workspace-token': 'synthetic-loopback-token', 'x-workspace-owner': 'user_loop' }, B = 'http://127.0.0.1:8763/internal/workspace/files';
const data = new Uint8Array(5_000_000); data.set([0,0,0,0x18,0x66,0x74,0x79,0x70], 0); data.fill(9, 8);
const form = new FormData(); form.append('file', new Blob([data]), 'clip.mp4');
const req = new Request('http://x', { method: 'POST', body: form });
const r = await fetch(B, { method: 'POST', headers: { ...H, 'content-type': req.headers.get('content-type') }, body: req.body, duplex: 'half' });
const j = await r.json(); if (r.status !== 201) throw new Error(r.status + JSON.stringify(j));
const g = await fetch(B + '/' + j.file.id + '/content', { headers: { ...H, range: 'bytes=4999990-' } });
const tail = new Uint8Array(await g.arrayBuffer());
console.log(JSON.stringify({ upload: r.status, size: j.file.size, range: g.status, content_range: g.headers.get('content-range'), tail_ok: tail.length === 10 && tail.every((b) => b === 9), uploads_remaining_today: j.quota.uploads_remaining_today }));
"""
out = subprocess.run(["node", "--input-type=module", "-e", JS], capture_output=True, text=True, timeout=60)
print(out.stdout.strip() or out.stderr[-2000:])
server.should_exit = True
sys.exit(out.returncode)
