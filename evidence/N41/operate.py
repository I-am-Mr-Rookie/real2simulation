"""SSH transport for N41. Never echo raw SSH failures or private job data."""
import base64
import hashlib
import json
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evidence/N38"))
from remote import remote


def execute(service, code):
    encoded = base64.b64encode(code.encode()).decode()
    output = remote(service, "python -c " + shlex.quote(f"import base64;exec(base64.b64decode('{encoded}'))")).decode()
    return json.loads(output[output.index("{"):])


def main(action):
    if action == "copy":
        result = execute("worker", (ROOT / "infra/railway/dev/redis_region_copy.py").read_text())
    elif action == "probe":
        result = execute("api", (ROOT / "evidence/N38/probe.py").read_text())
    elif action == "preflight":
        result = execute("worker", 'import os,json;from redis import Redis;'
                         'a=Redis.from_url(os.environ["REDIS_URL"]);b=Redis.from_url(os.environ["N41_DEST_REDIS_URL"]);'
                         'print(json.dumps({"source_keys":a.dbsize(),"destination_keys":b.dbsize(),'
                         '"destination_ping":b.ping(),"source_version":a.info("server")["redis_version"],'
                         '"destination_version":b.info("server")["redis_version"]}))')
    elif action == "unpause":
        result = execute("worker", 'import os,json;from redis import Redis;'
                         'a=Redis.from_url(os.environ["REDIS_URL"]);'
                         'print(json.dumps({"source_unpaused":a.execute_command("CLIENT","UNPAUSE")==b"OK"}))')
    elif action == "job":
        result = execute("api", '''
import os,json,urllib.request
from redis import Redis
r=Redis.from_url(os.environ["REDIS_URL"])
key=next(r.scan_iter(match="job:*:events"))
job=key.decode().split(":")[1]
owner=r.get(f"job:{job}:owner").decode()
request=urllib.request.Request("http://127.0.0.1:8080/internal/workspace/jobs/"+job,
    headers={"x-workspace-owner":owner,"x-workspace-token":os.environ["WORKSPACE_INTERNAL_TOKEN"]})
with urllib.request.urlopen(request,timeout=20) as response:
    data=json.load(response)
    assert data["job_id"]==job and isinstance(data["events"],list) and data["events"]
    print(json.dumps({"label":"MEASURED","http_status":response.status,
                      "job_id_matches":True,"events":len(data["events"]),"provenance_present":"provenance" in data}))
''')
    elif action == "restore":
        backup = ROOT.parent / "N38-orch282/evidence/N38/private/postgres-before.dump"
        data = backup.read_bytes()
        receipt = json.loads((ROOT / "evidence/N38/backup-receipt.json").read_text())
        if not data.startswith(b"PGDMP") or hashlib.sha256(data).hexdigest() != receipt["sha256"]:
            raise ValueError("Backup format/checksum mismatch")
        encoded = base64.b64encode(data).decode()
        command = 'set -eu; file=$(mktemp /tmp/n41-pg-XXXXXXXX.dump); printf %s ' + shlex.quote(encoded)
        command += ' | base64 -d > "$file"; pg_restore --list "$file" >/dev/null; '
        command += 'pg_restore --exit-on-error --single-transaction --no-owner --no-privileges -U "$PGUSER" -d "$PGDATABASE" "$file" >/dev/null; '
        command += """tables=$(psql -X -A -t -U "$PGUSER" -d "$PGDATABASE" -c "SELECT count(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema')"); test "$tables" = 0; printf '{"restored":true,"non_system_tables":0}'"""
        output = remote("de49f552-c641-45c9-8111-1d714c18f396", "sh -c " + shlex.quote(command)).decode()
        result = json.loads(output[output.index("{"):])
        result["backup_sha256"] = receipt["sha256"]
    else:
        raise ValueError("Unknown action")
    (Path(__file__).parent / f"{action}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "raw_output": "suppressed"}))
        raise SystemExit(1)
