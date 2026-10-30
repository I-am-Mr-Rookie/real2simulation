"""Independent structural and residual probes; offline, writes only to this review directory."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "evidence/S14")]


def audit(event, args):
    if event == "open":
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)):
            target = Path(os.fsdecode(path)).resolve()
            assert target.name != ".env", "no secret reads"
            writing = bool(mode and any(c in mode for c in "wax+")) or bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            assert not writing or target.is_relative_to(OUT), target


def denied(*a, **kw):
    raise AssertionError("offline: no network")


sys.addaudithook(audit)
socket.socket.connect = socket.create_connection = denied
from Build.agent import trial
from Build.agent.tools import safe_reply
from contracts.agent.validate import AgentContractError, CITE, numeric_issue, validate_response
import S14g_fix_oracle as oracle

baseline = json.loads((OUT / "results.json").read_text("utf-8"))
live = json.loads((ROOT / "evidence/S14/S14g-fix3-live.json").read_text("utf-8"))
tools, sid = live["turns"][0]["tool_outputs"], live["turns"][0]["scene_id"]
ref = {"type": "number", "ref": {"tool_output_id": tools[0]["id"], "quantity": "duration"}}


def check(text, expected, surface="segments", pieces=None):
    field = ([{"type": "text", "text": text}] if pieces is None else
             [{"type": "text", "text": p} for p in pieces]) + [copy.deepcopy(ref)]
    response = {"schema_version": "agent-response/1.0.0", "scene_id": sid,
                "segments": field if surface == "segments" else [copy.deepcopy(ref)], "questions": []}
    if surface == "rationale":
        response["candidates"] = [{"id": "candidate", "template": "free_fall", "rationale": field}]
    elif surface in ("prompt", "chip"):
        question = {"id": "q", "kind": "chips_and_free_text",
                    "prompt": [{"type": "text", "text": "Choose."}],
                    "chips": [{"id": "yes", "label": [{"type": "text", "text": "Yes."}]}]}
        if surface == "prompt":
            question["prompt"] = field
        else:
            question["chips"][0]["label"] = field
        response["questions"] = [question]
    error = None
    try:
        validate_response(response, tools, sid)
    except AgentContractError as exc:
        error = str(exc)
    visible = text + CITE
    oracle_error = oracle.oracle(visible)
    assert (error is None) == (oracle_error is None), (text, error, oracle_error)
    if expected is not None:
        assert (error is None) == expected, (text, surface, error)
    shown, blocked = safe_reply(response, tools, sid)
    assert bool(blocked) == bool(error)
    return {"text": text, "surface": surface, "accepted": error is None,
            "runtime_error": error, "oracle_error": oracle_error, "shown": shown}


matrix = []
amounts = "one ones a an single full whole half halves couple dozen several few both once pair".split()
for amount in amounts:
    for unit in ("seconds", "metres", "radians", "kilograms", "newtons", "ms"):
        for text in (f"The result is {amount} in {unit}: ",
                     f"The result in {unit} is {amount}. Tool result: "):
            matrix.append(check(text, False))

binding = []
for text in ("Elapsed time in seconds: ", "Elapsed time in seconds = ",
             "Elapsed time in seconds. Tool result: ", "Speed in metres per second: ",
             "This one fits the scene. ", "Please double-check the fit. "):
    binding.append(check(text, True))
for text in ("Elapsed time in seconds is ", "Elapsed time in seconds, ",
             "Elapsed time in seconds - ", "Elapsed time in seconds: approximately ",
             "The elapsed time in seconds is one: ", "The elapsed time in seconds:\none. "):
    for surface in ("segments", "prompt", "chip", "rationale"):
        binding.append(check(text, False, surface))

normalization = []
for text in ("The elapsed time is o\u200bne in seconds: ",
             "The elapsed time in sec\u00adonds is one: ",
             "The elapsed time is ＯＮＥ in ｓｅｃｏｎｄｓ: ",
             "The elapsed time is ONE in SECONDS: "):
    normalization.append(check(text, False))
text = "The elapsed time is one in seconds: "
for surface in ("segments", "prompt", "chip", "rationale"):
    normalization.append(check(text, False, surface, ["The elapsed time is o", "ne in sec", "onds: "]))

# Deliberately outside the bounded unit-clause guarantee; record behavior, not universal-English assertions.
residuals = [check(text, None) for text in (
    "Elapsed time in seconds. It is one. Tool result: ",
    "The duration is one. Tool result: ",
    "The sphere completes a single oscillation. Tool result: ",
    "The elapsed time is one microsecond. Tool result: ",
)]
for name, digest in baseline["protected_input_sha256"].items():
    with (ROOT / name).open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == digest, name
result = {"structural_matrix": matrix, "binding_controls": binding, "normalization_and_segments": normalization,
          "exploratory_residuals": residuals, "protected_files": len(baseline["protected_input_sha256"]),
          "protected_inputs_unchanged": True, "network_denied": True, "spend_usd": 0}
(OUT / "extension-results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"matrix": len(matrix), "binding": len(binding), "normalization": len(normalization),
                  "exploratory_residuals": residuals, "protected_inputs_unchanged": True}, indent=2))
