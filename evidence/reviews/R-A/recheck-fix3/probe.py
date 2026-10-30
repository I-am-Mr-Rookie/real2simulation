"""Offline R-A fix3 review. Run from this worktree: python -B evidence/reviews/R-A/recheck-fix3/probe.py.

Reads saved public-clip evidence only; denies sockets and new frame extraction.
Writes only beside this script. Assertions describe evidence, not a Gate A pass.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
import re
import socket
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "evidence/S14")]


def denied(*args, **kwargs):
    raise AssertionError("review forbids network or new frame extraction")


socket.socket.connect = denied
socket.create_connection = denied
import S14g_fix3_gate_a as gate  # noqa: E402
from contracts.agent.validate import AgentContractError, validate_response  # noqa: E402
from contracts.experiment.validate_experiment import validate  # noqa: E402

fix = gate.FIX
temporary_directory = tempfile.TemporaryDirectory
(OUT / "tmp").mkdir(exist_ok=True)
tempfile.TemporaryDirectory = lambda *args, **kwargs: temporary_directory(*args, **dict(kwargs, dir=OUT / "tmp"))
gate.understand.frame_jpeg = lru_cache(maxsize=32)(gate.understand.frame_jpeg)
gate.keyframes.extract = denied
gate.seek_frames = denied
gate.keyframes._run = denied


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


watched = sorted((ROOT / "evidence/S14").glob("S14g*"))
before = {str(p.relative_to(ROOT)): file_sha(p) for p in watched if p.is_file()}
live = read(ROOT / "evidence/S14/S14g-fix3-live.json")
saved_offline = read(ROOT / "evidence/S14/S14g-fix3-offline.json")
recorded = read(ROOT / "evidence/S14/S14g-fix3-recorded.json")
acq = {r["clip_id"]: r for r in read(ROOT / "evidence/clips/S02c-acquisition.json")["files"]}

# Exact original F1/F2 attacks, plus nearby explicit implicit-unit claims.
attacks = [
    ("original-one", ["Gravity is one metre per second squared."], True),
    ("original-double", ["Gravity is double the fitted value."], True),
    ("original-couple", ["Distance is a couple of metres."], True),
    ("original-split", ["Gravity is ni", "ne point ei", "ght metres per second squared."], True),
    ("implicit-second", ["The elapsed time is a second."], True),
    ("implicit-minute", ["The period is a minute."], True),
    ("implicit-radian", ["The angle is a radian."], True),
    ("ordinary-pronoun", ["This one fits the scene."], False),
    ("ordinary-double-check", ["Please double-check the fit."], False),
]
tools = live["turns"][0]["tool_outputs"]
sid = live["turns"][0]["scene_id"]
probes = []
for name, parts, invented in attacks:
    response = {"schema_version": "agent-response/1.0.0", "scene_id": sid, "questions": [],
                "segments": [{"type": "text", "text": s} for s in parts]}
    shown, blocked = fix.safe_reply(response, tools, sid)
    oracle_flag = fix.oracle("".join(parts)) is not None
    probes.append({"case": name, "known_invented": invented, "display_blocked": bool(blocked),
                   "original_text_displayed": "".join(parts) in shown, "oracle_flag": oracle_flag})
assert all(r["display_blocked"] and r["oracle_flag"] for r in probes[:4])
assert all(not r["display_blocked"] and not r["oracle_flag"] for r in probes[4:7])
assert all(not r["display_blocked"] and not r["oracle_flag"] for r in probes[7:])

# The same misses go through the actual trial/retry/display gate path, not only a helper.
end_to_end = []
for name, parts, _ in attacks[4:7]:
    response = {"schema_version": "agent-response/1.0.0", "scene_id": fix.OLD.SCENE_ID, "questions": [],
                "segments": [{"type": "text", "text": s} for s in parts] +
                [{"type": "number", "ref": {"tool_output_id": "gate-a-t00-fit", "quantity": "gravity"}}]}
    payload = fix.OLD.body(json.dumps(response))
    row = fix.turn(0, lambda _request: payload, fix.OLD.SCENE_ID)
    assert row["model_reply_shown"] and not row["blocked"] and row["invented"] is None
    end_to_end.append({"case": name, "attempts": row["attempts"], "model_reply_shown": True,
                       "oracle_flag": False, "blocked": False})

custody, spec_replay = [], []
assert len(live["specs"]) == len({s["case_id"] for s in live["specs"]}) == 10
assert len({s["source_sha256"] for s in live["specs"]}) == 10
for row in live["specs"]:
    clip = row["case_id"]
    source = gate.CANON / acq[clip]["local_path"]
    cache = Path(tempfile.gettempdir()) / "S14g-fix3-kf" / clip
    manifest_path = cache / "manifest.json"
    manifest = read(manifest_path)
    assert row["source_sha256"] == acq[clip]["sha256"] == file_sha(source)
    assert row["keyframe_manifest_sha256"] == file_sha(manifest_path)
    assert row["scene_sha256"] == fix.sha(row["scene_context"])
    assert row["licence"] == acq[clip]["licence"] and row["source_url"] == acq[clip]["source_url"]
    frames = gate.understand.sample(manifest["keyframes"], gate.FRAMES)
    assert row["frames"] == [{k: f[k] for k in ("index", "time_s", "time_source")} for f in frames]
    custody.append({"case_id": clip, "acquisition_and_source_hash_match": True,
                    "manifest_hash_match": True, "context_hash_match": True,
                    "frame_selection_match": True,
                    "sampled_frame_sha256": [file_sha(cache / f["file"]) for f in frames],
                    "seek_manifest": manifest.get("kind") == "seek_frames"})
    accepted = validate_response(row["accepted_text"], (), row["scene_id"])
    assert accepted == row["accepted_response"]
    assert recorded[clip] == row["accepted_text"]
    assert validate(row["spec"]) == row["spec"]
    base = fix.tsv.fixture(row["template"])
    base["scene"]["scene_id"] = row["scene_id"]
    try:
        gate.interview.answers_to_spec(base, None, None, row["answers"])
    except (AgentContractError, ValueError, TypeError, KeyError):
        production_without_bundle_refuses = True
    else:
        production_without_bundle_refuses = False
    assert production_without_bundle_refuses
    spec_replay.append({"case_id": clip, "numeric_contract_valid": True,
                        "accepted_response_revalidates": True, "production_without_bundle_refuses": True,
                        "scene_scale_inherited_from_test_fixture": row["spec"]["scene"]["scale_status"] == base["scene"]["scale_status"],
                        "environment_inherited_from_test_fixture": row["spec"]["environment"] == base["environment"],
                        "answers_equal_synthetic_fixture": all(v == fix.SYNTHETIC_ANSWERS[row["template"]][k]
                                                                 for k, v in row["answers"].items())})

# Re-run the existing offline FUNCTION, not its CLI (CLI writes into evidence/S14).
replayed = gate.run("offline")
replayed2 = gate.run("offline")
assert replayed["summary"] == replayed2["summary"] == saved_offline["summary"]
assert all(replayed["summary"][key] == live["summary"][key] for key in
           ("gate_a", "distinct_recorded_scenes", "valid_recorded_specs", "turns", "invented_shown_oracle"))
assert replayed["specs"] == replayed2["specs"] == saved_offline["specs"] == live["specs"]
assert set(replayed["spec_sources"].values()) == {"recorded"}

turns = []
for row in live["turns"]:
    outputs = row["tool_outputs"]
    assert fix.sha(outputs) == row["tool_outputs_sha256"]
    response = validate_response(row["accepted_response"], outputs, row["scene_id"])
    shown, blocked = fix.safe_reply(response, outputs, row["scene_id"])
    assert shown == row["shown"] and not blocked
    # Reference validation above + an independent residual scan; no format-only provenance waiver.
    formats = [f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})"
               for output in outputs for q in output["quantities"].values()]
    residual = shown
    for text in formats:
        residual = residual.replace(text, " ")
    assert fix.oracle(residual) is None
    assert all(fix.oracle(text) is None for text in fix.visible_strings(response))
    turns.append({"case_id": row["case_id"], "mystery": row["mystery"],
                  "tools_sha_match": True, "exact_render_replayed": True, "residual_oracle_clean": True})

# Key-name-only hygiene. Do not search or print credential values or arbitrary large payloads.
secret_key = re.compile(r"api[_-]?key|authorization|bearer|secret|password|access[_-]?token|refresh[_-]?token|private[_-]?key", re.I)


def key_hits(obj, path="$"):
    hits = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = path + "." + key
            if secret_key.search(key):
                hits.append(here)
            hits.extend(key_hits(value, here))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            hits.extend(key_hits(value, f"{path}[{i}]"))
    elif isinstance(obj, str) and obj.lstrip().startswith(("{", "[")):
        try:
            nested = json.loads(obj)
        except (ValueError, TypeError):
            pass
        else:
            hits.extend(key_hits(nested, path + ".<embedded-json>"))
    return hits


assert key_hits({"nested": {"api_key": "redacted-test"}}) == ["$.nested.api_key"]
assert key_hits({"input_tokens": 1, "keyframes": []}) == []
hygiene = []
for p in sorted((ROOT / "evidence/S14").glob("S14g-fix*.json*")):
    docs = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line] if p.suffix == ".jsonl" else [read(p)]
    hits = [hit for doc in docs for hit in key_hits(doc)]
    hygiene.append({"file": p.name, "bytes": p.stat().st_size, "credential_shaped_key_paths": hits})
assert not any(r["credential_shaped_key_paths"] for r in hygiene)
assert before == {str(p.relative_to(ROOT)): file_sha(p) for p in watched if p.is_file()}

result = {"oracle_corpus": fix.self_check(), "original_and_new_probes": probes,
          "new_misses_through_trial_path": end_to_end, "custody": custody, "spec_replay": spec_replay,
          "offline_summary_matches_saved": True, "offline_specs_deterministic": True,
          "offline_full_turns_deterministic": replayed["turns"] == replayed2["turns"],
          "offline_turns_are_scripted_not_live_response_replay": True,
          "live_turn_exact_response_replay": turns, "key_name_hygiene": hygiene,
          "source_evidence_unchanged": True, "source_sha256": before,
          "network_denied": True, "new_extraction_denied": True}
(OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"original_attacks_closed": 4, "new_common_unit_claim_misses": len(end_to_end),
                  "recorded_clip_custody": len(custody), "numeric_specs": len(spec_replay),
                  "live_turns_exact_replayed": len(turns), "hygiene_files": len(hygiene),
                  "offline_full_turns_deterministic": result["offline_full_turns_deterministic"],
                  "source_evidence_unchanged": True}, indent=2))
