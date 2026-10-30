"""S14g-fix independent invented-number oracle for Gate A counting (R-A F1/F2).

Deliberately does NOT import contracts.agent (the validator under test): its own token lexicon and
unicodedata.numeric, run on the final VISIBLE string after the exact trusted quantity renderings are removed.
Finite coverage, not an unbypassable-language guarantee; self-checked on the shared adversarial corpus.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[2] / "tests/agent/fixtures/adversarial-visible-text.json"
WORDS = set("""zero two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen
seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion
dozen half halves quarter quarters percent twice thrice triple tripled quadruple doubled couple third thirds fourth
fifth sixth seventh eighth ninth tenth tenths hundredths""".split())
UNITS = set("""metre metres meter meters centimetre centimetres centimeter centimeters millimetre millimetres
kilometre kilometres kilogram kilograms gram grams newton newtons joule joules watt watts hertz kg cm mm km m""".split())
TIME = {"second", "seconds", "minute", "minutes", "hour", "hours", "degree", "degrees", "s"}
MORE = {"as", "the", "larger", "smaller", "greater", "bigger", "more", "less"}


def oracle(visible: str) -> str | None:
    """Why the visible text states a number no tool cites, or None."""
    for ch in visible:
        if unicodedata.numeric(ch, None) is not None:
            return f"numeral {ch!r}"
    norm = unicodedata.normalize("NFKC", visible).lower()
    return _scan(norm) or _scan("".join(c for c in norm if unicodedata.category(c) != "Cf"))


def _scan(text: str) -> str | None:
    toks = [(m.group(0), m.end()) for m in re.finditer(r"[a-z]+", text)]
    for i, (tok, end) in enumerate(toks):
        nxt = toks[i + 1][0] if i + 1 < len(toks) else ""
        prev = toks[i - 1][0] if i else ""
        if tok in WORDS or (tok == "double" and text[end:end + 1] != "-") or (tok == "pair" and nxt == "of"):
            return f"word {tok!r}"
        if tok == "times" and nxt in MORE or tok == "point" and (prev in WORDS | {"one"} or nxt in WORDS | {"one"}):
            return f"phrase {prev} {tok} {nxt}"
        if tok == "one" and (nxt in UNITS | TIME) or tok in ("a", "an") and nxt in UNITS:
            return f"implicit one {tok} {nxt}"
    return None


def visible(shown: str, rendered_quantities) -> str:
    for q in rendered_quantities:
        shown = shown.replace(q, " ")
    return shown


def self_check() -> dict:
    cases = json.loads(CORPUS.read_text(encoding="utf-8"))["cases"]
    wrong = [cid for cid, parts, bad in cases
             if (oracle("".join(" " if p is None else p for p in parts)) is not None) != bad]
    assert not wrong, f"oracle disagrees with corpus: {wrong}"
    return {"corpus_cases": len(cases), "oracle_agrees": True}


if __name__ == "__main__":
    print(self_check())

