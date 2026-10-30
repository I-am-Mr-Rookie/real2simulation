"""S13i: /internal/workspace upload + job routes via TestClient. Offline; no GPU, Modal, AWS or Meta call.

Upload bytes are a visibly SYNTHETIC mp4-shaped blob; the RM04 replay reads the real recorded S13h evidence.
Replay output is RECORDED (S13h-orch46), not a live run, Gate R or physical evidence.
"""
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api.workspace import analysis
from Build.api.workspace.jobs import (LABEL, RECORDING, UNDERSTAND_LABEL, UNDERSTOOD, approved_shas, create_router,
                                      load_recording, load_understanding, recorded_runner, scene_resolver, shell_scene)
from Build.pipeline.jobs import MemoryStore
from Build.pipeline.uploads import UploadService

ROOT = Path(__file__).resolve().parents[2]
TOKEN, OWNER, OTHER = "synthetic-test-token", "user_synthA", "user_synthB"
AUTH = {"x-workspace-token": TOKEN, "x-workspace-owner": OWNER}
OTHER_AUTH = {**AUTH, "x-workspace-owner": OTHER}
BLOB = b"\x00\x00\x00\x18ftypmp42" + b"SYNTHETIC-S13i-test-bytes" * 40
BLOB_SHA = hashlib.sha256(BLOB).hexdigest()
RM04_SHA = "8231fbca041d030f2fc39bd4281af6112e476bf811f548fc9019db53f7cb87ec"
RM04_SPEC_UTC = "2026-10-30T05:06:04Z"  # S14g-fix3 ledger, call spec-RM04
NO_NET = "test must not open network connections"
_CONNECT = socket.socket.connect


def loopback_only(sock, addr):
    """Windows asyncio uses a loopback socketpair internally; anything else (Meta, Modal, AWS) fails the test."""
    if not (isinstance(addr, tuple) and addr[0] in ("127.0.0.1", "::1")):
        raise AssertionError(f"{NO_NET}: {addr!r}")
    return _CONNECT(sock, addr)


class JobsRouterTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"WORKSPACE_INTERNAL_TOKEN": TOKEN})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # Recording copy re-keyed to the synthetic blob so the route path is exercised without the 25 MB clip.
        self.rec = self.tmp / "rec"
        shutil.copytree(RECORDING / "keyframes", self.rec / "keyframes")
        timing = json.loads((RECORDING / "timing.json").read_text(encoding="utf-8"))
        timing["stages"][1]["result"]["sha256"] = BLOB_SHA
        (self.rec / "timing.json").write_text(json.dumps(timing), encoding="utf-8")
        # Same re-key for the recorded S14g-fix3 RM04 understand spec (ledger copied unchanged).
        self.und = self.tmp / UNDERSTOOD.name
        live = json.loads(UNDERSTOOD.read_text(encoding="utf-8"))
        rm04 = [s for s in live["specs"] if s["case_id"] == "RM04"]
        rm04[0]["source_sha256"] = BLOB_SHA
        self.und.write_text(json.dumps({"specs": rm04}), encoding="utf-8")
        ledger = UNDERSTOOD.with_name(UNDERSTOOD.name.replace("-live.json", "-ledger.jsonl"))
        shutil.copy(ledger, self.tmp / ledger.name)
        self.client = self.app(self.rec)

    def app(self, recording, understood=None):
        app = FastAPI()
        self.store = MemoryStore()
        und = understood or self.und
        app.include_router(create_router(self.store, UploadService(self.tmp / "up"),
                                         lambda: {BLOB_SHA: "SYNTH", RM04_SHA: "RM04"}, recording, und))
        app.include_router(analysis.create_router(scene_resolver(self.store, und)))  # as S04m will inject it
        return TestClient(app)

    def code(self, r, status):
        self.assertEqual(r.status_code, status, r.text)
        return r.json()["detail"]["code"]

    def upload(self, client=None, headers=AUTH):
        c = client or self.client
        r = c.post("/internal/workspace/uploads", headers=headers,
                   json={"media_type": "video/mp4", "size_bytes": len(BLOB), "sha256": BLOB_SHA})
        self.assertEqual(r.status_code, 200, r.text)
        return r.json()["upload_id"]

    def finish(self, client=None):
        c = client or self.client
        uid = self.upload(c)
        self.assertEqual(c.put(f"/internal/workspace/uploads/{uid}/chunks/0", headers=AUTH, content=BLOB).status_code, 200)
        r = c.post(f"/internal/workspace/uploads/{uid}/complete", headers=AUTH)
        self.assertEqual(r.status_code, 200, r.text)
        return r.json()

    def test_auth_required(self):
        self.assertEqual(self.code(self.client.get("/internal/workspace/jobs/job_" + "0" * 32), 401), "UNAUTHORIZED")

    def test_resumable_upload_and_unapproved_sha(self):
        r = self.client.post("/internal/workspace/uploads", headers=AUTH,
                             json={"media_type": "video/mp4", "size_bytes": 10, "sha256": "a" * 64})
        self.assertEqual(self.code(r, 422), "INVALID_INPUT")
        uid = self.upload()
        url = f"/internal/workspace/uploads/{uid}"
        self.assertEqual(self.client.get(url, headers=AUTH).json()["committed_bytes"], 0)  # resume point
        ack = self.client.put(f"{url}/chunks/0", headers=AUTH, content=BLOB).json()
        self.assertEqual((ack["committed_bytes"], ack["duplicate"]), (len(BLOB), False))
        again = self.client.put(f"{url}/chunks/0", headers=AUTH, content=BLOB).json()  # retried after a lost ack
        self.assertTrue(again["duplicate"])
        self.assertEqual(self.client.get(url, headers=AUTH).json()["committed_bytes"], len(BLOB))
        bad = self.client.put(f"{url}/chunks/7", headers=AUTH, content=b"x")
        self.assertEqual(self.code(bad, 422), "INVALID_INPUT")
        self.assertEqual(self.client.post(f"{url}/complete", headers=AUTH).json()["upload"]["status"], "complete")

    def test_other_owner_gets_404(self):
        uid = self.upload()
        for r in (self.client.get(f"/internal/workspace/uploads/{uid}", headers=OTHER_AUTH),
                  self.client.put(f"/internal/workspace/uploads/{uid}/chunks/0", headers=OTHER_AUTH, content=BLOB),
                  self.client.post(f"/internal/workspace/uploads/{uid}/complete", headers=OTHER_AUTH)):
            self.assertEqual(self.code(r, 404), "NOT_FOUND")
        job_id = self.finish()["job"]["job_id"]
        self.assertEqual(self.code(self.client.get(f"/internal/workspace/jobs/{job_id}", headers=OTHER_AUTH), 404), "NOT_FOUND")
        self.assertEqual(self.code(self.client.get("/internal/workspace/jobs/job_" + "f" * 32, headers=AUTH), 404), "NOT_FOUND")

    def test_recorded_replay_labelled_with_original_utc(self):
        out = self.finish()
        self.assertEqual(out["provenance"]["label"], LABEL)
        self.assertFalse(out["provenance"]["live"])
        labels = out["provenance"]["stage_labels"]
        self.assertEqual(labels.pop("understand"), UNDERSTAND_LABEL)  # never live, never S13h
        self.assertEqual(set(labels.values()), {LABEL})
        self.assertEqual(out["provenance"]["understand"]["recorded_utc"], RM04_SPEC_UTC)
        self.assertFalse(out["provenance"]["understand"]["live"])
        doc = self.client.get(f"/internal/workspace/jobs/{out['job']['job_id']}", headers=AUTH).json()
        rows = doc["events"]
        self.assertEqual([(e["stage"], e["status"]) for e in rows[:4]],
                         [("validate", "started"), ("validate", "succeeded"), ("keyframes", "started"), ("keyframes", "succeeded")])
        # Original S13h UTC timestamps, unchanged apart from +00:00 -> Z.
        self.assertEqual([e["ts"] for e in rows[:4]], ["2026-10-29T21:44:56.313Z", "2026-10-29T21:44:56.384Z",
                                                       "2026-10-29T21:44:56.385Z", "2026-10-29T21:44:57.424Z"])
        # understand carries the S14g-fix3 ledger UTC; segment resumes with the original S13h UTC.
        self.assertEqual([(e["stage"], e["status"], e["ts"]) for e in rows[4:7]],
                         [("understand", "started", RM04_SPEC_UTC), ("understand", "succeeded", RM04_SPEC_UTC),
                          ("segment", "started", "2026-10-29T21:44:57.425Z")])
        self.assertEqual(doc["job"]["status"], "ready")
        after = self.client.get(f"/internal/workspace/jobs/{out['job']['job_id']}?after=4", headers=AUTH).json()
        self.assertEqual([e["revision"] for e in after["events"]], list(range(5, 13)))

    def test_without_recorded_understand_replay_stops_honestly(self):
        out = self.finish(self.app(self.rec, self.tmp / "absent.json"))
        self.assertEqual((out["job"]["status"], out["job"]["error"]["code"]), ("failed", "DEPENDENCY_UNAVAILABLE"))
        self.assertIn("understand was not run", out["job"]["error"]["message"])
        self.assertNotIn("understand", out["provenance"]["stage_labels"])
        r = self.client.get(f"/internal/workspace/scenes/{out['job']['job_id']}/questions", headers=AUTH)
        self.assertEqual(self.code(r, 404), "NOT_FOUND")  # failed job: no scene

    def test_scene_resolver_owner_scoped_questions_and_spec(self):
        job_id = self.finish()["job"]["job_id"]
        rm04 = json.loads(self.und.read_text(encoding="utf-8"))["specs"][0]
        q = self.client.get(f"/internal/workspace/scenes/{job_id}/questions", headers=AUTH)
        self.assertEqual(q.status_code, 200, q.text)
        self.assertEqual(q.json(), analysis.interview.questions(job_id, rm04["spec"]["template"]))
        for path in ("questions", "spec"):
            r = (self.client.get if path == "questions" else self.client.post)(
                f"/internal/workspace/scenes/{job_id}/{path}", headers=OTHER_AUTH,
                **({} if path == "questions" else {"json": {"answers": rm04["answers"]}}))
            self.assertEqual(self.code(r, 404), "NOT_FOUND")
        # Recorded scene_context is not an authoritative bundle: owner Q16=A numeric-contract path (S14j), labelled.
        s = self.client.post(f"/internal/workspace/scenes/{job_id}/spec", headers=AUTH, json={"answers": rm04["answers"]})
        self.assertEqual(s.status_code, 200, s.text)
        self.assertEqual((s.json()["label"], s.json()["setup_validated"]), ("scale unverified, not setup-validated", False))
        resolve = scene_resolver(self.store, self.und)
        self.assertEqual(resolve(OWNER, job_id)[0], rm04["spec"])
        self.assertIsNone(resolve(OTHER, job_id))
        self.assertIsNone(resolve(OWNER, "job_" + "f" * 32))

    def test_web_spec_body_rm04_200_and_old_array_body_422(self):  # S15q: live 422 root cause
        job_id = self.finish()["job"]["job_id"]
        body = json.loads((ROOT / "tests/workspace/fixtures/rm04-spec-body.json").read_text(encoding="utf-8"))  # pinned by spec-body.test.mjs
        s = self.client.post(f"/internal/workspace/scenes/{job_id}/spec", headers=AUTH, json=body)
        self.assertEqual(s.status_code, 200, s.text)
        self.assertEqual((s.json()["label"], s.json()["spec"]["parameters"]["drop_height"]["value"]), ("scale unverified, not setup-validated", 1.5))
        old = [{"questionId": "drop_height", "chipId": None, "text": "1.5"},  # pre-S15q web body (interviewAnswers() verbatim)
               {"questionId": "initial_vertical_velocity", "chipId": "at-rest", "text": None}]
        r = self.client.post(f"/internal/workspace/scenes/{job_id}/spec", headers=AUTH, json={"answers": old})
        self.assertEqual(self.code(r, 422), "INVALID_INPUT")

    def test_missing_recording_is_dependency_unavailable(self):
        out = self.finish(self.app(self.tmp / "absent"))
        self.assertEqual(out["job"]["status"], "failed")
        self.assertEqual(out["job"]["error"]["code"], "DEPENDENCY_UNAVAILABLE")
        self.assertEqual(out["provenance"]["recorded_stages"], [])

    def test_real_rm04_recording_and_approval(self):
        rec = load_recording(RM04_SHA)
        self.assertEqual(sorted(rec), ["keyframes", "package", "reconstruct", "segment", "validate"])
        self.assertEqual(rec["segment"][:2], ("2026-10-29T21:44:57.425Z", "2026-10-29T21:46:11.904Z"))
        self.assertEqual(load_recording("b" * 64), {})
        spec, utc = load_understanding(RM04_SHA)
        self.assertEqual((spec["case_id"], spec["valid"], utc), ("RM04", True, RM04_SPEC_UTC))
        self.assertIsNone(load_understanding("b" * 64))
        shas = approved_shas()
        self.assertEqual(shas.get(RM04_SHA), "RM04")
        self.assertNotIn("df46212c259bf4504fb822a182965f4e73771a93e8cd120e83dfd6b00ee1091c", shas)  # FF01: not granted
        runner, prov = recorded_runner(MemoryStore(), RM04_SHA)
        snap = runner.run("job_" + "1" * 32, RM04_SHA, shell_scene("job_" + "1" * 32))
        self.assertEqual(snap["status"], "ready")
        self.assertEqual(prov["stage_labels"]["understand"], UNDERSTAND_LABEL)
        self.assertEqual(runner.events("job_" + "1" * 32)[1]["output_sha256"], RM04_SHA)

    def test_recorded_executor_never_spends(self):
        blocked = {m: None for m in ("modal", "boto3", "botocore")}  # import -> ImportError
        with mock.patch.dict(sys.modules, blocked), \
                mock.patch.object(socket.socket, "connect", loopback_only), \
                mock.patch.object(subprocess, "Popen", side_effect=AssertionError("no process launch")):
            self.assertEqual(self.finish()["job"]["status"], "ready")
        probe = ("import sys; from Build.api.workspace.jobs import recorded_runner, shell_scene; from Build.pipeline.jobs import MemoryStore;"
                 "r,_=recorded_runner(MemoryStore(), '" + RM04_SHA + "'); r.run('job_' + '2'*32, '" + RM04_SHA + "', shell_scene('x'));"
                 "print(sorted(m for m in sys.modules if m.split('.')[0] in ('modal','boto3','botocore','requests')"
                 " or m in ('Build.pipeline.understand','Build.pipeline.gpu_stages','Build.pipeline.e2e')))")
        p = subprocess.run([sys.executable, "-B", "-c", probe], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual((p.returncode, p.stdout.strip()), (0, "[]"), p.stderr)
        src = (ROOT / "Build/api/workspace/jobs.py").read_text(encoding="utf-8")
        for name in ("modal", "boto3", "gpu_stages", "understand", "urllib", "requests", "httpx", "subprocess"):
            self.assertNotRegex(src, rf"(?m)^\s*(import|from)\s+\S*{name}")


if __name__ == "__main__":
    unittest.main()

