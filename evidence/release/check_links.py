"""S25a: every relative Markdown link in README.md and ATTRIBUTION.md must resolve. Run from repo root."""
import pathlib, re, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
bad = []
for doc in ("README.md", "ATTRIBUTION.md"):
    for target in re.findall(r"\]\(([^)\s]+)\)", (ROOT / doc).read_text(encoding="utf-8")):
        if re.match(r"[a-z]+:|#", target):
            continue
        path = urllib.parse.unquote(target.split("#")[0])
        if not (ROOT / path).exists():
            bad.append(f"{doc}: {target}")
assert re.findall(r"\]\(([^)\s]+)\)", "[a](b%20c.md)") == ["b%20c.md"]  # self-check of the link regex
print("\n".join(bad) or "all relative links resolve")
sys.exit(1 if bad else 0)
