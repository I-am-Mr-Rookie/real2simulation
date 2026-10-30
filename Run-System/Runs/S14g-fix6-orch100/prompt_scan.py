"""S14g-fix6: list code-owned string literals (Build/agent, Build/pipeline) that fix5 accepted but fix6 refuses."""
import ast
import glob
import re
import sys

sys.path.insert(0, ".")
import contracts.agent.validate as v  # noqa: E402

NEW = v._BOUND
OLD = re.compile(NEW.pattern + rf"|(?:\b{v._LINK}\b{v._GAP})+[:=]{v._GAP}{v.CITE}", re.I)  # fix5 label chain


def issue(text, bound):
    v._BOUND = bound
    try:
        return v.numeric_issue(text)
    finally:
        v._BOUND = NEW


hits = 0
for path in glob.glob("Build/agent/*.py") + glob.glob("Build/pipeline/*.py"):
    for node in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value + v.CITE  # worst case: a citation follows the literal
            if issue(text, OLD) is None and issue(text, NEW) is not None:
                hits += 1
                print(path, repr(node.value)[:120])
print("code_owned_literals_newly_refused", hits)

