"""S14g-fix7: list code-owned string literals (Build/agent, Build/pipeline) that main (fix6) accepted but fix7 refuses."""
import ast
import glob
import subprocess
import sys

sys.path.insert(0, ".")
import contracts.agent.validate as new  # noqa: E402

old = {"__file__": new.__file__, "__name__": "fix6_validate"}  # main's validator, same schema paths
exec(compile(subprocess.run(["git", "show", "main:contracts/agent/validate.py"], capture_output=True, text=True,
                            encoding="utf-8", check=True).stdout, new.__file__, "exec"), old)

hits = 0
for path in glob.glob("Build/agent/*.py") + glob.glob("Build/pipeline/*.py"):
    for node in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for text in (node.value, node.value + new.CITE):  # bare, and worst case: a citation follows the literal
                if old["numeric_issue"](text) is None and new.numeric_issue(text) is not None:
                    hits += 1
                    print(path, repr(node.value)[:120], new.numeric_issue(text))
print("code_owned_literals_newly_refused", hits)

