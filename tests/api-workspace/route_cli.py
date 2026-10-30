"""S15t: post one JSON body (stdin) to a REAL analysis route via FastAPI TestClient; print {status, body}. Used by node contract tests."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(os.path.dirname(HERE)), HERE]
os.environ['WORKSPACE_INTERNAL_TOKEN'] = __import__('test_analysis').TOKEN
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from Build.api.workspace.analysis import create_router  # noqa: E402
import test_spec_q16 as t  # noqa: E402

app = FastAPI(); app.include_router(create_router(t.resolver))
r = TestClient(app).post('/internal/workspace/' + sys.argv[1], headers={**t.AUTH, 'content-type': 'application/json'},
                         content=sys.stdin.buffer.read())
sys.stdout.write(json.dumps({'status': r.status_code, 'body': r.json()}))
