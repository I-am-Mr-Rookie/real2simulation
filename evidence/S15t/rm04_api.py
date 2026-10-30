"""S15t: post the real RM04 what-if fit request through the real /fit and /report routes (FastAPI TestClient)."""
import json, os, sys
sys.path[:0] = ['.', 'tests/api-workspace']
os.environ['WORKSPACE_INTERNAL_TOKEN'] = __import__('test_analysis').TOKEN
from fastapi import FastAPI
from fastapi.testclient import TestClient
from Build.api.workspace.analysis import create_router
import test_spec_q16 as t
app = FastAPI(); app.include_router(create_router(t.resolver)); c = TestClient(app)
req = json.load(open('evidence/S15t/rm04-fit-request.json', encoding='utf-8'))
f = c.post('/internal/workspace/fit', headers=t.AUTH, json=req['fit'])
print('fit', f.status_code, file=sys.stderr)
rep = c.post('/internal/workspace/report', headers=t.AUTH, json={'spec': req['spec'], 'fit': f.json(), 'label': req['what_if_label']})
print('report', rep.status_code, json.dumps(rep.json())[:600] if rep.status_code != 200 else rep.json()['status'], file=sys.stderr)
json.dump(f.json(), open('evidence/S15t/rm04-fit-response.json', 'w', encoding='utf-8'), indent=1)
