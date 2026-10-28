"""Regenerate RUNS.md (Koushik's run checklist) from QUEUE.md.

Usage: python Run-System/runs_view.py
QUEUE.md stays the source of truth. Never edit RUNS.md by hand; change the
task's Status or Retry holds in QUEUE.md and run this script.
"""
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "QUEUE.md"
STATE = ROOT / "STATE.md"
OUT = ROOT / "RUNS.md"
DHAKA = timezone(timedelta(hours=6))
STATUSES = {"TODO", "IN PROGRESS", "PARTIAL", "BLOCKED", "DONE"}
TOOL = {"CODEX-1": "Codex", "CODEX-2": "Codex", "CLAUDE": "Codex (native Claude)", "KOUSHIK": "You"}
BOX = {"DONE": "[x]", "IN PROGRESS": "[~]", "PARTIAL": "[~]", "BLOCKED": "[!]", "TODO": "[ ]"}


def load():
    text = QUEUE.read_text(encoding="utf-8")
    tasks, titles = [], {}
    in_table = False
    for line in text.splitlines():
        if line.startswith("| ID | Lane"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("| "):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            deps = [d for d in re.split(r"[;,]\s*", c[6]) if d and d != "—"]
            status = c[9].upper()
            if status not in STATUSES:
                raise SystemExit(f"Unknown status {c[9]!r} for {c[0]} in QUEUE.md")
            tasks.append(dict(id=c[0], lane=c[1], model=c[2], step=c[3], mins=c[4],
                              title=c[5], deps=deps, status=status))
        elif in_table:
            in_table = False
        m = re.match(r"### (S\d\d) — (.+)", line)
        if m:
            titles[m.group(1)] = m.group(2).strip()
    return tasks, titles


def open_questions():
    """Unanswered '- [ ]' lines under STATE.md's '## Owner questions' heading."""
    out, inside = [], False
    for line in STATE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.startswith("## Owner questions")
        elif inside and line.lstrip().startswith("- [ ]"):
            out.append(line.strip())
    return out


def load_retry_holds(task_ids):
    """Explicit UTC cooldowns, not inferred from prose or remote availability."""
    holds, inside = {}, False
    for line in QUEUE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line == "## Retry holds"
        elif inside and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] == "Run" or cells[0].startswith("---"):
                continue
            if len(cells) != 3 or cells[0] not in task_ids or cells[0] in holds:
                raise ValueError(f"Invalid or duplicate retry hold: {line}")
            task_id, timestamp, reason = cells
            deadline = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if deadline.tzinfo is None or deadline.utcoffset() != timedelta(0) or not reason:
                raise ValueError(f"Retry hold needs an explicit UTC deadline and reason: {line}")
            holds[task_id] = (deadline, reason)
    return holds


def main():
    tasks, titles = load()
    questions = open_questions()
    by_id = {t["id"]: t for t in tasks}
    holds = load_retry_holds(by_id)
    current = datetime.now(timezone.utc)
    done = {t["id"] for t in tasks if t["status"] == "DONE"}
    steps_done = {s for s in {t["step"] for t in tasks}
                  if all(t["status"] == "DONE" for t in tasks if t["step"] == s)}

    def dep_ok(d):
        return d in done if d in by_id else d in steps_done

    def cooling(t):
        return (t["status"] in {"TODO", "PARTIAL"} and t["id"] in holds
                and current < holds[t["id"]][0])

    def ready(t):
        return (t["status"] in {"TODO", "PARTIAL"} and not cooling(t)
                and all(dep_ok(d) for d in t["deps"]))

    def line(t, settings=True):
        model = t["model"].replace(" / ", ", effort ")
        extra = f" — {TOOL[t['lane']]} · {model}" if settings and t["lane"] != "KOUSHIK" else ""
        note = {"IN PROGRESS": " *(in progress)*", "PARTIAL": " *(partial: resume it)*",
                "BLOCKED": " *(blocked: see STATE.md)*"}.get(t["status"], "")
        if t["id"] in holds and t["status"] in {"TODO", "PARTIAL"}:
            deadline, reason = holds[t["id"]]
            when = (deadline.strftime("%b %d, %H:%M UTC") + " / "
                    + deadline.astimezone(DHAKA).strftime("%b %d, %H:%M Dhaka"))
            note = (f" *(retry held until {when}; {reason})*" if cooling(t) else
                    f" *(bounded retry eligible; source recovery unverified; {reason})*")
        return f"- {BOX[t['status']]} **{t['id']}**{extra} — {t['title']} ({t['mins']} min){note}"

    # Fillers (step FILLER) never crowd out real work; they sit in their own section.
    agent_ready = [t for t in tasks if ready(t) and t["lane"] != "KOUSHIK" and t["step"] != "FILLER"]
    owner_ready = [t for t in tasks if ready(t) and t["lane"] == "KOUSHIK"]
    active = [t for t in tasks if t["status"] == "IN PROGRESS"]
    blocked = [t for t in tasks if t["status"] == "BLOCKED"]
    waiting_retry = [t for t in tasks if cooling(t)]
    now = current.astimezone(DHAKA).strftime("%b %d, %H:%M")

    o = ["# Runs checklist", "",
         f"Updated {now} Dhaka from QUEUE.md by `Run-System/runs_view.py`. Agents regenerate this file; don't edit it by hand.", "",
         "**How to run one:** open the tool and model shown, then say `Complete run S05a` (or `Complete the next run`).",
         "All lanes run inside Codex; CLAUDE uses the existing native Claude route, not Claude Code (owner correction Oct29). Manual runs: no fixed agent cap; independent isolated shards only, serialized shared controls/heavy builds (PARALLELISM_POLICY.md).", "",
         f"Progress: **{len(done)} / {len(tasks)}** runs done · {len(active)} in progress · {len(blocked)} blocked · "
         f"{len(owner_ready)} waiting for Koushik · {len(questions)} open reviews", "",
         "## Reviews for Koushik", ""]
    o += questions or ["None open. Routine decisions proceed; necessary owner inputs come from STATE.md."]
    o += ["",
         "## Ready now", ""]
    for lane in ("CODEX-1", "CODEX-2", "CLAUDE"):
        rows = [t for t in agent_ready if t["lane"] == lane]
        o.append(f"**{lane}**")
        if not rows:
            o.append("- Nothing ready yet: check dependencies and retry holds below.")
        o += [line(t) for t in rows[:3]]
        if len(rows) > 3:
            o.append(f"- …and {len(rows) - 3} more ready in this lane")
        o.append("")
    if active:
        o += ["## In progress", ""] + [line(t) for t in active] + [""]
    if waiting_retry:
        o += ["## Waiting to retry", ""] + [line(t) for t in waiting_retry] + [""]
    o += ["## Waiting for Koushik", ""]
    o += ([line(t) for t in owner_ready] if owner_ready else ["Nothing right now."])
    o += [""]
    if blocked:
        o += ["## Blocked", ""] + [line(t) for t in blocked] + [""]
    o += ["## All runs by step", "",
          "Legend: [x] done · [~] in progress or partial · [!] blocked · [ ] to do", ""]
    for step in sorted({t["step"] for t in tasks}):
        rows = [t for t in tasks if t["step"] == step]
        n = sum(t["status"] == "DONE" for t in rows)
        o.append(f"<details><summary><b>{step}</b> — {titles.get(step, '')} ({n}/{len(rows)})</summary>")
        o.append("")
        o += [line(t) for t in rows]
        o += ["", "</details>", ""]
    OUT.write_text("\n".join(o), encoding="utf-8")
    print(f"RUNS.md: {len(done)}/{len(tasks)} done, {len(agent_ready)} ready, {len(owner_ready)} for Koushik")


if __name__ == "__main__":
    main()
