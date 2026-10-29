"""S14f mutation spot checks: each mutant must fail tests.agent.test_reply. Usage: python S14f_mutation.py <root>"""
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
M = [("untraced reply shown, not replaced", "Build/agent/tools.py",
      "return render(tool_backed(scene_id, tool_outputs), tool_outputs, scene_id), list(error.issues)", "raise"),
     ("replacement drops tool values", "Build/agent/tools.py", "    for output in tool_outputs:\n", "    for output in ():\n"),
     ("digit quantity name leaks into text", "Build/agent/tools.py",
      'words if numeric_issue(words) is None else "value"', "words"),
     ("'one point five' not caught", "contracts/agent/validate.py", r"one\s+point|", ""),
     ("ordinals not caught", "contracts/agent/validate.py", "third|", ""),
     ("fallback built without the validated outputs", "Build/agent/tools.py",
      "    except AgentContractError as error:\n        return render(tool_backed",
      "    except AgentContractError as error:\n        tool_outputs = []\n        return render(tool_backed")]
for name, rel, old, new in M:
    f = root / rel; orig = f.read_text(encoding="utf-8")
    try:
        assert orig.count(old) == 1, name
        f.write_text(orig.replace(old, new), encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.agent.test_reply"], cwd=root, capture_output=True, text=True)
        print(("KILLED" if r.returncode else "SURVIVED"), "-", name, "|", r.stderr.strip().splitlines()[-1])
    finally:
        f.write_text(orig, encoding="utf-8")
