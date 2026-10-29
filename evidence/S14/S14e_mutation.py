"""S14e mutation spot checks: each mutant of Build/agent/trial.py must fail tests.agent.test_trial. Usage: python S14e_mutation.py <root>"""
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]); f = root / "Build/agent/trial.py"; orig = f.read_text(encoding="utf-8")
M = [("uncited claim accepted", [('if not any(segment["type"] == "number"', 'if False and not any(segment["type"] == "number"')]),
     ("questions/candidates accepted", [('if response["questions"] or response.get("candidates"):', "if False:")]),
     ("fitter id not trial-specific", [('fit_tool_output(f"{trial_id}-fit", fit)', 'fit_tool_output("trial-fit", fit)')]),
     ("simulator value fabricated", [('quantity(last["position_m"], "m")', 'quantity(1.0, "m")')]),
     ("retries not counted after first attempt", [("range(1 + MAX_RETRIES)", "range(MAX_RETRIES)")]),
     ("retry omits validator feedback", [("build_check_request(context, rejected[-1] if rejected else ())", "build_check_request(context, ())")]),
     ("fallback adds an untraced claim", [('". Simulated, not physical evidence."', '". Gravity is about ten; simulated."')]),
     ("transport errors retried", [("        body = post(build_check_request(context, rejected[-1] if rejected else ()))\n        try:\n",
                                    "        try:\n            body = post(build_check_request(context, rejected[-1] if rejected else ()))\n"),
                                   ("except AgentContractError as error:\n            rejected.append(list(error.issues))",
                                    "except Exception as error:\n            rejected.append([str(error)])")])]
try:
    for name, edits in M:
        src = orig
        for old, new in edits:
            assert src.count(old) == 1, name
            src = src.replace(old, new)
        f.write_text(src, encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.agent.test_trial"], cwd=root, capture_output=True, text=True)
        print(("KILLED" if r.returncode else "SURVIVED"), "-", name, "|", r.stderr.strip().splitlines()[-1])
finally:
    f.write_text(orig, encoding="utf-8")
