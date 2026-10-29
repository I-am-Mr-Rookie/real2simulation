import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); f = root / "Build/agent/muse.py"; orig = f.read_text(encoding="utf-8")
M = [("off-by-one: MAX_RETRIES = 4", "MAX_RETRIES = 3 ", "MAX_RETRIES = 4 "),
     ("retries not counted after first attempt", "range(1 + MAX_RETRIES)", "range(MAX_RETRIES)"),
     ("retry omits validator feedback", "feedback=rejected[-1] if rejected else ()", "feedback=()"),
     ("candidate-free valid reply returned (no ask)", "(response if response.get(\"candidates\") else ask_user(context[\"scene_id\"]))", "response"),
     ("transport errors retried", "        body = post(build_request(context, feedback=rejected[-1] if rejected else ()))\n        try:\n            response = validate_response(output_text(body), (), context[\"scene_id\"])\n        except AgentContractError as error:\n            rejected.append(list(error.issues))",
      "        try:\n            body = post(build_request(context, feedback=rejected[-1] if rejected else ()))\n            response = validate_response(output_text(body), (), context[\"scene_id\"])\n        except Exception as error:\n            rejected.append([str(error)])"),
     ("fallback fabricates a candidate", '"candidates": [],', '"candidates": [{"id": "guess", "template": "free_fall", "rationale": text("Probably a drop.")}],'),
     ("fallback skips validation", "    return validate_response({\n        \"schema_version\": RESPONSE_VERSION, \"scene_id\": scene_id,\n        \"segments\": text(\"I could not", "    return (lambda r, *_: r)({\n        \"schema_version\": RESPONSE_VERSION, \"scene_id\": scene_id,\n        \"segments\": text(\"I could not")]
try:
    for name, old, new in M:
        assert orig.count(old) == 1, name
        f.write_text(orig.replace(old, new), encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.agent.test_retry"], cwd=root, capture_output=True, text=True)
        print(("KILLED" if r.returncode else "SURVIVED"), "-", name, "|", r.stderr.strip().splitlines()[-1])
finally:
    f.write_text(orig, encoding="utf-8")

