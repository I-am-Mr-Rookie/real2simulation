import json, os, sys
sys.path[:0] = ['.', 'tests/api-workspace']
os.environ['WORKSPACE_INTERNAL_TOKEN'] = __import__('test_analysis').TOKEN
from fastapi import FastAPI
from fastapi.testclient import TestClient
from Build.api.workspace.analysis import create_router
import test_spec_q16 as t
app = FastAPI(); app.include_router(create_router(t.resolver)); c = TestClient(app)
body = json.load(open('tests/workspace/fixtures/rm04-spec-body.json', encoding='utf-8'))
r = c.post(f'/internal/workspace/scenes/{t.RM04}/spec', headers=t.AUTH, json=body)
print(r.status_code, file=sys.stderr)
os.makedirs('evidence/S15r', exist_ok=True)
json.dump(r.json(), open('evidence/S15r/rm04-spec-response.json', 'w', encoding='utf-8'), indent=1)

