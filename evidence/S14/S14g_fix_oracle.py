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
TIME = {"second", "seconds", "minute", "minutes", "hour", "hours", "degree", "degrees", "s",
        # S14g-fix4 (R-A F1-R): angles and short time forms
        "millisecond", "milliseconds", "ms", "min", "hr", "h", "radian", "radians", "rad", "deg"}
MORE = {"as", "the", "larger", "smaller", "greater", "bigger", "more", "less"}
# S14g-fix5 (R-A F1-R2): structural unit binding, independent of contracts.agent. Every unit token must be bound to a
# cited quantity (CITE) directly after it, or sit in an amount-free "in <units>" phrase ("in metres per second",
# "in metres: <q>"). Else: invented. fix6 (R-A F1-R3): bare label chains ("one whole minute: <q>") no longer bind.
CITE = "\ue000"  # what visible()/visible_strings put where a trusted quantity was rendered
ALL_UNITS = UNITS | TIME | set("""millimeter millimeters kilometer kilometers centigram milligram milligrams pascal
pascals sec secs day days revolution revolutions inch inches foot feet yard yards mile miles pound pounds lb lbs gee gees
ft hz pa g n j w""".split())
LINK = ALL_UNITS | {"per", "squared", "cubed", "or"}
# S14g-fix7 (R-A F1-R4): a clause (split at . ! ? ;) holding any unit token may hold no amount token at all.
AMOUNT = {"one", "ones", "a", "an", "single", "full", "whole", "half", "halves", "couple", "dozen", "several", "few",
          "both", "once", "pair"}
ENDS = {".", "!", "?", ";"}


def oracle(visible: str) -> str | None:
    """Why the visible text states a number no tool cites, or None."""
    for ch in visible:
        if unicodedata.numeric(ch, None) is not None:
            return f"numeral {ch!r}"
    norm = unicodedata.normalize("NFKC", visible).lower()
    return _scan(norm) or _scan("".join(c for c in norm if unicodedata.category(c) != "Cf"))


def _scan(text: str) -> str | None:
    toks = [(m.group(0), m.start(), m.end()) for m in re.finditer(rf"[a-z]+|{CITE}|[.!?;:=]", text)]
    clause_amount, clause_unit = None, False
    for i, (tok, start, end) in enumerate(toks):
        nxt = toks[i + 1][0] if i + 1 < len(toks) else ""
        prev = toks[i - 1][0] if i else ""
        if tok in ENDS:
            clause_amount, clause_unit = None, False
        is_unit = tok in ALL_UNITS and text[start - 1:start] not in ("'", "’", ".") and text[end:end + 1] not in ("'", "’")
        clause_unit = clause_unit or is_unit
        clause_amount = clause_amount or (tok if tok in AMOUNT else None)
        if clause_unit and clause_amount:
            return f"amount {clause_amount!r} in unit clause"
        if tok in WORDS or (tok == "double" and text[end:end + 1] != "-") or (tok == "pair" and nxt == "of"):
            return f"word {tok!r}"
        if tok == "times" and nxt in MORE or tok == "point" and (prev in WORDS | {"one"} or nxt in WORDS | {"one"}):
            return f"phrase {prev} {tok} {nxt}"
        if tok in ("one", "a", "an", "single") and nxt in UNITS | TIME:  # fix4: a/an + time/angle too
            return f"implicit one {tok} {nxt}"
        if is_unit and not _bound(toks, i, text):
            return f"unbound unit {tok}"
    return None


def _bound(toks: list, i: int, text: str) -> bool:
    j = i - 1  # "<q> metres per second" / "in metres per second": only link words back (a word or "." breaks it)
    while j >= 0 and toks[j][0] in LINK:
        j -= 1
    if j < 0 or toks[j][0] not in (CITE, "in"):
        return False
    k = i  # fix7: "in <units>" binds only if the chain is directly followed (optional ":"/"=") by CITE or clause end
    while k + 1 < len(toks) and toks[k + 1][0] in LINK:
        k += 1
    return toks[j][0] == CITE or re.match(rf"\s*[:=]?\s*(?:{CITE}|[.!?;]|$)", text[toks[k][2]:]) is not None


def visible(shown: str, rendered_quantities) -> str:
    for q in rendered_quantities:
        shown = shown.replace(q, CITE)
    return shown


def self_check() -> dict:
    cases = json.loads(CORPUS.read_text(encoding="utf-8"))["cases"]
    wrong = [cid for cid, parts, bad in cases
             if (oracle("".join(CITE if p is None else p for p in parts)) is not None) != bad]
    assert not wrong, f"oracle disagrees with corpus: {wrong}"
    return {"corpus_cases": len(cases), "oracle_agrees": True}


if __name__ == "__main__":
    print(self_check())

