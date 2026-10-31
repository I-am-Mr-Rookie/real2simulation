"""S13i: /internal/workspace upload + job routes via TestClient. Offline; no GPU, Modal, AWS or Meta call.

Upload bytes are a visibly SYNTHETIC mp4-shaped blob; the RM04 replay reads the real recorded S13h evidence.
Replay output is RECORDED (S13h-orch46), not a live run, Gate R or physical evidence.
"""
import hashlib
import importlib.util
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
from Build.api.workspace.jobs import (LABEL, OWNER_CLIPS, RECORDING, UNDERSTAND_LABEL, UNDERSTOOD, approved_shas, create_router, owner_clips,
                                      load_recording, load_understanding, owner_measurement, recorded_runner, scene_resolver, shell_scene)
from Build.pipeline.jobs import MemoryStore
from Build.pipeline.uploads import UploadService

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("s15aa_sync", ROOT / "evidence/S15aa/sync_owner_measurements.py")
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)
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
        base = analysis.interview.questions(job_id, rm04["spec"]["template"])
        self.assertEqual(q.json(), {**base, "questions": [*base["questions"], analysis.KNOWN_SIZE]})
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
        self.assertNotIn("measurement", out["provenance"])  # not an owner clip

    def owner_app(self, clip):
        app = FastAPI()
        self.store = MemoryStore()
        app.include_router(create_router(self.store, UploadService(self.tmp / "up"), lambda: {BLOB_SHA: clip},
                                         self.tmp / "absent", self.und, owners=lambda: {BLOB_SHA: clip}))
        app.include_router(analysis.create_router(scene_resolver(self.store, self.und)))
        return TestClient(app)

    def test_owner_clip_recorded_measurement_or_abstain(self):  # S15v
        out = self.finish(self.owner_app("OWN01"))
        m = out["provenance"]["measurement"]
        self.assertEqual((m["status"], m["g"], m["u"], m["unit"]), ("recorded", 10.96, 0.77, "m/s^2"))
        self.assertEqual((m["input_label"], m["source"]), ("OWNER_RECORDED / RECORDED", "evidence/S07/S07m/results.json"))
        self.assertTrue(m["measured_label"].startswith("MEASURED"))
        self.assertIn("Held-out check FAIL: chi2/dof = 12.28/3 = 4.09, p = 0.0065", m["caveat"])  # S15aa: S07m v3, not 6 px
        for s in ("THIRD, post-hoc", "forking-paths", "Scale user-declared", "phone clock not externally verified"):
            self.assertIn(s, m["caveat"])
        self.assertNotIn("6 px", m["caveat"])
        self.assertNotIn(">>", m["caveat"])
        self.assertEqual(m["scale"], {"reference": "book cover horizontal edge in fall plane", "value_m": 0.2028,
                                      "label": "user-declared, not verified"})
        c = self.owner_app("OWN10")
        out = self.finish(c)
        self.assertEqual((out["provenance"]["measurement"]["status"], out["provenance"]["measurement"]["label"]),
                         ("abstain", "UNCERTAIN: no measurement"))
        self.assertIn("v1 abstain (S07h)", out["provenance"]["measurement"]["message"])
        doc = c.get(f"/internal/workspace/jobs/{out['job']['job_id']}", headers=AUTH).json()  # persists for polling
        self.assertEqual(doc["provenance"]["measurement"]["status"], "abstain")

    def test_owner_clip_no_scene_job_then_known_size_interview_then_result(self):  # S15y
        c = self.owner_app("OWN01")
        out = self.finish(c)
        job_id = out["job"]["job_id"]
        self.assertEqual(out["job"], {"job_id": job_id, "status": "no_scene",
                                      "label": "no scene: owner clip, scene reconstruction not run"})
        self.assertNotIn("DEPENDENCY_UNAVAILABLE", json.dumps(out))  # no failure anywhere for an owner clip
        self.assertEqual((out["provenance"]["executor"], out["provenance"]["recorded_stages"]), ("none", []))
        doc = c.get(f"/internal/workspace/jobs/{job_id}", headers=AUTH).json()
        self.assertEqual((doc["kind"], doc["job"]["status"], doc["events"]), ("job_progress", "no_scene", []))
        q = c.get(f"/internal/workspace/scenes/{job_id}/questions", headers=AUTH)
        self.assertEqual(q.json(), {"schema_version": "agent-response/1.0.0", "scene_id": job_id, "questions": [analysis.KNOWN_SIZE]})
        s = c.post(f"/internal/workspace/scenes/{job_id}/spec", headers=AUTH,
                   json={"answers": {"known_size": {"text": "book cover edge, 20.28 cm"}}}).json()
        self.assertEqual((s["owner_clip"], s["measurement"]["g"], s["measurement"]["u"]), (True, 10.96, 0.77))
        self.assertEqual((s["user_scale"]["status"], s["user_scale"]["length_m"]), ("declared", 0.2028))
        for other in ("questions", "spec"):  # owner-scoped
            r = (c.get if other == "questions" else c.post)(f"/internal/workspace/scenes/{job_id}/{other}", headers=OTHER_AUTH,
                                                             **({} if other == "questions" else {"json": {"answers": {}}}))
            self.assertEqual(self.code(r, 404), "NOT_FOUND")
        c2 = self.owner_app("OWN10")
        j2 = self.finish(c2)["job"]["job_id"]
        s2 = c2.post(f"/internal/workspace/scenes/{j2}/spec", headers=AUTH, json={"answers": {}}).json()  # no size: abstain, not 422
        self.assertEqual((s2["measurement"]["label"], s2["user_scale"]["status"]), ("UNCERTAIN: no measurement", "abstain"))

    def test_owner_clips_match_evidence_and_are_approved(self):  # tracked copy must equal the S07g/S07i evidence
        reg = json.loads((ROOT / "evidence/S07/S07g/clips-sha256.json").read_text(encoding="utf-8"))
        clips = json.loads(OWNER_CLIPS.read_text(encoding="utf-8"))["clips"]
        self.assertEqual({c: e["sha256"] for c, e in clips.items()}, {c: reg[c]["sha256"] for c in clips})
        self.assertTrue(all(e["r_frame_rate"] == "30/1" and e["height"] > e["width"] for e in clips.values()))  # 30 fps portrait
        # S15aa: every stored number/label re-derived from S07m/S07h evidence JSON (v1 only, never v2)
        self.assertEqual({c: (e.get("measurement"), e.get("abstain")) for c, e in clips.items()},
                         {c: (sync.measurement_of(c, e["scale_value_m"]) if not sync.abstain_of(c) else None, sync.abstain_of(c))
                          for c, e in clips.items()})
        measured = {c for c, e in clips.items() if "measurement" in e}
        self.assertEqual(measured, {"OWN01", "OWN02", "OWN03", "OWN04", "OWN05", "OWN07", "OWN08", "OWN09"})
        self.assertEqual({c for c, e in clips.items() if "abstain" in e}, {"OWN06", "OWN10", "OWN11", "OWN12"})
        s07m = json.loads((ROOT / "evidence/S07/S07m/results.json").read_text(encoding="utf-8"))
        for c in measured:  # stored values equal the evidence values (rounded as displayed) and are labelled
            row = next(r for r in s07m["rows"] if r["clip"] == c and r["analysis"] == "v1")
            m = clips[c]["measurement"]
            self.assertEqual((m["g"], m["u"], m["v3"]["chi2"], m["v3"]["dof"], m["v3"]["verdict"]),
                             (round(row["g"], 2), round(row["u"], 2), round(row["chi2"], 2), row["dof"], "PASS" if row["v3_pass"] else "FAIL"))
            self.assertAlmostEqual(m["v3"]["p"], row["p"], delta=row["p"] * 0.03)
            self.assertEqual(m["source_sha256"], hashlib.sha256((ROOT / m["source"]).read_bytes()).hexdigest())
            self.assertTrue(m["measured_label"].startswith("MEASURED") and m["unit"] == "m/s^2")
            cav = owner_measurement(c)["caveat"]
            self.assertIn(f"Held-out check {m['v3']['verdict']}", cav)
            self.assertEqual("not accuracy" in cav, m["v3"]["verdict"] == "PASS")
        shas = approved_shas()
        self.assertEqual(shas.get(clips["OWN01"]["sha256"]), "OWN01")
        self.assertEqual(owner_clips(), {e["sha256"]: c for c, e in clips.items()})

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

