# UI-e-orch88 evidence helper: serve this worktree, borrowing three from the canonical checkout node_modules (worktree has none).
import http.server as h,functools,os
R=r'C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon'
class H(h.SimpleHTTPRequestHandler):
    def translate_path(s,p):
        q=p.split('?')[0]
        return os.path.join(R,q.lstrip('/')) if q.startswith('/Build/web/node_modules/') else super().translate_path(p)
h.ThreadingHTTPServer(('127.0.0.1',3190),functools.partial(H,directory=os.getcwd())).serve_forever()
