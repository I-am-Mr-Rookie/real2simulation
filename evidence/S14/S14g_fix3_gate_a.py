"""S14g-fix3 Gate A over the 10 owner-approved recorded clips (R-A F3/F4). Usage (repo root):
    python evidence/S14/S14g_fix3_gate_a.py offline|live

- One case per approved clip (evidence/owner/S02/APPROVAL.md), case_id = clip id, never repeated.
- Scene input: S13c keyframes of the licensed clip -> S13e clip_context + sampled keyframe images (number-free).
- live: one Wonder keyframe call per clip (+1 retry on contract rejection) via S14g-fix live_post (per-call
  ledger, run cap, $120 hard stop minus $30 reserve); accepted output text saved to S14g-fix3-recorded.json.
  offline: replays that recorded file (scripted labelled stub if absent: plumbing only, never gate evidence).
- Spec validity = interview answers -> contracts.experiment validate() (numeric spec contract). The authoritative
  bundle check validate_setup() is UNAVAILABLE for real clips: no scene bundle with known scale exists (S05d
  abstained). Recorded per case; the summary scope says so.
- Turns: the S14g-fix 30 Spark turns (actual simulator/fitter, tool outputs + sha persisted for re-audit).
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import S14g_fix_gate_a as FIX  # noqa: E402  (reuse: oracle, visible_strings, turn, summary, live_post, ledger)
from Build.agent import interview, muse  # noqa: E402
from Build.agent.interview import answers_to_spec, questions, template_of  # noqa: E402
from Build.pipeline import keyframes, understand  # noqa: E402
from contracts.agent.validate import AgentContractError, validate_response  # noqa: E402
from contracts.experiment.validate_experiment import validate  # noqa: E402

ROOT, OLD = FIX.ROOT, FIX.OLD
CANON = Path(r"C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")  # gitignored clips, read-only
FIX.RID, FIX.CAP_USD, FIX.LEDGER = "S14g-fix3-orch64", 2.50, HERE / "S14g-fix3-ledger.jsonl"
CLIPS = ["RM02", "RM04", "RM05", "PD02", "PD03", "PD04", "PD06", "PJ03", "ST03", "BN01"]  # APPROVAL.md
FRAMES = 3  # frugal: first/middle/last keyframe
RECORDED = HERE / "S14g-fix3-recorded.json"
ACQ = {f["clip_id"]: f for f in json.loads((ROOT / "evidence/clips/S02c-acquisition.json").read_text(encoding="utf-8-sig"))["files"]}
BUNDLE = "unavailable: no authoritative scene bundle with known scale for this real clip (validate_setup not run)"


def clip_input(clip):
    """Licensed clip -> (manifest, sampled frames, image parts). Keyframes go to %TEMP%, never into Git."""
    out = Path(tempfile.gettempdir()) / "S14g-fix3-kf" / clip
    src = CANON / ACQ[clip]["local_path"]
    if keyframes._sha256(src) != ACQ[clip]["sha256"]:
        raise ValueError(f"{clip}: source sha256 differs from S02c acquisition record")
    if (out / "manifest.json").exists():
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    else:
        try:
            manifest = keyframes.extract(clip, src, out, CANON / "clips.csv")
        except keyframes.UploadError:  # upload duration policy (e.g. RM02 15 min): seek 3 evenly spaced frames instead
            manifest = seek_frames(clip, src, out)
    frames = understand.sample(manifest["keyframes"], FRAMES)
    parts = [{"type": "input_image", "image_url": understand._data_url("image/jpeg", understand.frame_jpeg(out / f["file"]))}
             for f in frames]
    return manifest, frames, parts, hashlib.sha256((out / "manifest.json").read_bytes()).hexdigest()


def seek_frames(clip, src, out):
    duration = float(keyframes._probe(src, "-show_entries", "format=duration")["format"]["duration"])
    out.mkdir(parents=True, exist_ok=True)
    kfs = []
    for i, t in enumerate(duration * f for f in (0.1, 0.5, 0.9)):
        name = f"seek_{i}.jpg"
        keyframes._run(["ffmpeg", "-v", "error", "-nostdin", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
                        "-q:v", "2", str(out / name)])
        kfs.append({"index": i, "file": name, "time_s": round(t, 3), "time_source": "ffmpeg-seek(container duration)"})
    manifest = {"kind": "seek_frames", "provenance": keyframes.provenance(clip, src, CANON / "clips.csv"),
                "source": {"file": src.name, "sha256": ACQ[clip]["sha256"]}, "keyframes": kfs}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def spec_only(spec, _scene, _root):
    validate(spec)  # numeric spec contract; authoritative-bundle validate_setup unavailable for real clips
    return spec


def spec_case(clip, post) -> dict:
    sid = clip.lower()  # spec scene_id pattern is lowercase; case_id keeps the clip id
    row = {"case_id": clip, "scene_id": sid, "synthetic": False, "source_sha256": ACQ[clip]["sha256"],
           "licence": ACQ[clip]["licence"], "source_url": ACQ[clip]["source_url"], "valid": False, "bundle_bound": BUNDLE}
    manifest, frames, parts, msha = clip_input(clip)
    context = understand.clip_context(manifest, sid)
    row.update(keyframe_manifest_sha256=msha, scene_sha256=hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest(),
               scene_context=context, frames=[{k: f[k] for k in ("index", "time_s", "time_source")} for f in frames])
    body = understand.build(context, parts, "keyframe images in time order")
    texts, response, rejected = [], None, []
    for _ in range(2):
        texts.append(muse.output_text(post(body)))
        try:
            response = validate_response(texts[-1], (), sid)
            break
        except AgentContractError as error:
            rejected.append(list(error.issues)[:8])
    row.update(attempts=len(texts), rejected=rejected, model_number_attempts=OLD.model_numbers([OLD.body(t) for t in texts]),
               accepted_text=texts[-1] if response else None, accepted_response=response)
    if response is None:
        return dict(row, why="no contract-valid Wonder reply in 2 attempts")
    row["invented"] = [o for o in map(FIX.oracle, FIX.visible_strings(response)) if o]
    if not response.get("candidates"):
        return dict(row, why="no candidate -> ask_user")
    template = template_of(response, response["candidates"][0]["id"])
    asked = [q["id"] for q in questions(sid, template)["questions"]]
    answers = {k: v for k, v in FIX.SYNTHETIC_ANSWERS[template].items() if k in asked}
    spec = FIX.tsv.fixture(template)
    spec["scene"].update(scene_id=sid)
    real, interview.validate_setup = interview.validate_setup, spec_only
    try:
        built = answers_to_spec(spec, None, None, answers)
        return dict(row, valid=True, template=template, answers=answers, spec=built)
    except (AgentContractError, KeyError, ValueError) as error:
        return dict(row, template=template, answers=answers, why=getattr(error, "issues", None) or str(error))
    finally:
        interview.validate_setup = real


def recorded_post(clip):
    rec = json.loads(RECORDED.read_text(encoding="utf-8")) if RECORDED.exists() else {}
    if clip in rec:
        return lambda _req: OLD.body(rec[clip]), "recorded"
    stub = {"schema_version": "agent-response/1.0.0", "scene_id": clip.lower(), "questions": [],
            "segments": [{"type": "text", "text": "Plumbing stub, not a model reply."}],
            "candidates": [{"id": "drop", "template": "free_fall", "rationale": [{"type": "text", "text": "Stub only."}]}]}
    return lambda _req: OLD.body(json.dumps(stub)), "stub"


def run(mode) -> dict:
    specs, turns, stop, sources = [], [], None, {}
    try:
        for clip in CLIPS:
            post, sources[clip] = (FIX.live_post(f"spec-{clip}"), "live") if mode == "live" else recorded_post(clip)
            specs.append(spec_case(clip, post))
        if mode == "live":
            for i in range(FIX.TURNS):
                turns.append(FIX.turn(i, FIX.live_post(f"turn-{i:02d}"), OLD.SCENE_ID))
        else:
            turns = [FIX.turn(i, lambda _r, s=script: s.pop(0), OLD.SCENE_ID) for i, script in enumerate(OLD.synthetic_turns())]
    except (FIX.Budget, RuntimeError) as error:
        stop = str(error)
    if mode == "live":
        old = json.loads(RECORDED.read_text(encoding="utf-8")) if RECORDED.exists() else {}
        old.update({s["case_id"]: s["accepted_text"] for s in specs if s.get("accepted_text")})
        RECORDED.write_text(json.dumps(old, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    result = {"spec_sources": sources, "specs": specs, "turns": turns, "stopped": stop}
    summ = FIX.summary(result)
    if "stub" in sources.values():
        summ.update(gate_a="NOT_MET", why="stub replies present: plumbing only")
    summ["scope"] = ("spec validity = numeric spec contract validate(); authoritative-bundle validate_setup unavailable "
                     "for real clips (no known-scale scene bundles); turns on synthetic-room-v1 tool outputs")
    if summ["gate_a"] == "MET":  # S14g-fix4 (R-A F3-R): numeric-contract scope is never Gate A MET
        summ.update(gate_a="PROVISIONAL", why="numeric-contract scope only; real validate_setup path: see S14g_fix4_gate_a.py")
    result["summary"] = summ
    return result


if __name__ == "__main__":
    mode = sys.argv[1]
    result = run(mode)
    (HERE / f"S14g-fix3-{mode}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=1))
