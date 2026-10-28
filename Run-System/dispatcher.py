"""Local, bounded worker scheduler. Standard library only. No product implementation."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid

LANES = ("CODEX-1", "CODEX-2", "CLAUDE")
MARKER = "S03 harmless dispatcher verification\n"
SOURCE = Path(__file__).resolve().parent
QUOTA = re.compile(
    r"insufficient_quota|rate_limit_error|rate_limit_exceeded|"
    r"usage_limit_reached|quota[_ ](?:exceeded|exhausted)|"
    r"(?:usage|rate) limit.{0,50}(?:reached|exceeded)|"
    r"hit your (?:usage )?limit|out of (?:extra )?usage|\b429\b",
    re.I,
)

@dataclass
class Task:
    id: str
    lane: str
    model: str
    step: str
    minutes: int
    title: str
    depends: list[str]
    owns: list[str]
    acceptance: str
    status: str

def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *map(str, args)],
        check=True, capture_output=True, text=True, timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    ).stdout.strip()

def read_queue(path):
    tasks = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("|"):
            continue
        a = [x.strip() for x in line.split("|")[1:-1]]
        if len(a) != 10 or a[1] not in (*LANES, "KOUSHIK"):
            continue
        t = Task(a[0], a[1], a[2], a[3], int(a[4]), a[5],
                 [] if a[6] == "—" else a[6].split(", "),
                 a[7].split("; "), a[8], a[9])
        if not re.fullmatch(r"[A-Za-z0-9-]+", t.id):
            raise ValueError("Unsafe task ID")
        if not 0 < t.minutes <= 30:
            raise ValueError("Task timebox exceeds 30 minutes")
        for own in t.owns:
            path = Path(own)
            if path.is_absolute() or ".." in path.parts or ":" in own or "\\" in own:
                raise ValueError("Owns paths must be safe repository-relative paths")
        tasks.append(t)
    if not tasks or len({t.id for t in tasks}) != len(tasks):
        raise ValueError("Queue missing or duplicate IDs")
    validate_dependencies(tasks)
    return tasks

def dependency_ids(task, tasks):
    ids = {t.id for t in tasks}
    result = []
    for dep in task.depends:
        if dep in ids:
            result.append(dep)
        else:
            members = [t.id for t in tasks if t.step == dep]
            if not members:
                raise ValueError("Unknown dependency: " + dep)
            result.extend(members)
    return result

def validate_dependencies(tasks):
    graph = {t.id: dependency_ids(t, tasks) for t in tasks}
    seen, active = set(), set()
    def visit(x):
        if x in active:
            raise ValueError("Dependency cycle: " + x)
        if x in seen:
            return
        active.add(x)
        for d in graph[x]:
            visit(d)
        active.remove(x)
        seen.add(x)
    for x in graph:
        visit(x)

def overlap(a, b):
    return any(x.rstrip("/") == y.rstrip("/")
               or x.endswith("/") and y.startswith(x)
               or y.endswith("/") and x.startswith(y)
               for x in a.owns for y in b.owns)

def approval_ready(task, state):
    """Exact recorded approval gates, not conclusions inferred from task prose."""
    required = []
    if task.step == "S22" and task.id != "S22a":
        required.append("judging candidate approval")
    if task.id in {"S22c", "S22d", "S22e"}:
        required.append("fresh qa identities ready")
    if task.step == "S23" and task.lane != "KOUSHIK":
        required.append("judging promotion approval")
    if task.id == "S24j":
        required.append("public video approval")
    if task.id == "S25e":
        required.append("public repo approval")
    return all(state.get(key, "").upper() == "YES" for key in required)

def select_ready(tasks, active, capacity=2):
    if capacity not in (1, 2):
        raise ValueError("At most two processes")
    busy = {x.lane for x in active}
    occupied = list(active)
    done = {t.id for t in tasks if t.status == "DONE"}
    chosen = []
    for task in tasks:
        if len(occupied) >= capacity:
            break
        if task.lane not in LANES or task.lane in busy or task.status != "TODO":
            continue
        if not set(dependency_ids(task, tasks)) <= done:
            continue
        if any(overlap(task, a) for a in occupied):
            continue
        chosen.append(task)
        occupied.append(task)
        busy.add(task.lane)
    return chosen

def read_state(path):
    out = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        a = [x.strip() for x in line.split("|")[1:-1]]
        if len(a) == 2:
            out[a[0].lower()] = a[1]
    return out

def write_state(path, values):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    pending = dict(values)
    for i, line in enumerate(lines):
        a = [x.strip() for x in line.split("|")[1:-1]]
        if len(a) == 2 and a[0] in pending:
            lines[i] = f"| {a[0]} | {pending.pop(a[0])} |"
    if pending:
        lines.extend(["", "## Dispatcher checkpoint", "", "| Field | Value |", "|---|---|"])
        lines.extend(f"| {k} | {v} |" for k, v in pending.items())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def set_status(path, task_id, status):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    found = False
    for i, line in enumerate(lines):
        a = line.split("|")
        if len(a) == 12 and a[1].strip() == task_id:
            a[-2] = " " + status + " "
            lines[i] = "|".join(a)
            found = True
            break
    if not found:
        raise ValueError("Queue changed: task disappeared")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_command(task, config, resolver=shutil.which, read_only=False):
    name, effort = task.model.rsplit(" / ", 1)
    allowed = {"CODEX-1": {"GPT-6.1 Sol"},
               "CODEX-2": {"GPT-6.1 Sol", "GPT-6.1 Terra"},
               "CLAUDE": {"Opus 5.5", "Sonnet 5.5", "Haiku 5.5"}}
    if name not in allowed.get(task.lane, set()):
        raise ValueError("Unapproved lane/model pair")
    expected = {"GPT-6.1 Sol": {"medium", "high", "xhigh"},
                "GPT-6.1 Terra": {"high"}, "Opus 5.5": {"medium"},
                "Sonnet 5.5": {"high"}, "Haiku 5.5": {"high"}}
    if effort not in expected[name]:
        raise ValueError("Unapproved effort")
    model = config["models"].get(name)
    if not model or not re.fullmatch(r"[A-Za-z0-9._/-]+", model):
        raise ValueError("Missing or unsafe configured exact model ID")
    if task.lane.startswith("CODEX"):
        exe = config.get("codex_executable") or resolver("codex.exe") or resolver("codex")
        sandbox = "read-only" if read_only else config.get("codex_sandbox", "read-only")
        if sandbox not in {"read-only", "workspace-write"}:
            raise ValueError("Only read-only or scoped workspace-write is permitted")
        if sandbox == "workspace-write" and config.get("codex_workspace_write_approved") is not True:
            raise ValueError("Scoped workspace-write requires explicit owner approval")
        args = ["exec", "--sandbox", sandbox, "--model", model, "-c",
                'model_reasoning_effort="' + effort + '"', "--json", "-"]
    else:
        exe = config.get("claude_executable") or resolver("claude.exe") or resolver("claude")
        args = ["-p", "--model", model, "--effort", effort,
                "--output-format", "stream-json", "--verbose"]
    if not exe or Path(exe).suffix.lower() in (".cmd", ".bat", ".ps1"):
        raise ValueError("Native CLI executable required; no shell wrapper or auto-install")
    return [str(exe), *args]

def quota_event(line):
    try:
        item = json.loads(line)
    except (ValueError, TypeError):
        return bool(QUOTA.search(line))
    if not isinstance(item, dict):
        return False
    typ = str(item.get("type", "")).lower()
    error = item.get("error")
    if typ == "rate_limit_event":
        info = item.get("rate_limit_info", {})
        return info.get("status") in {"rejected", "exceeded", "over_limit"}
    if error or "error" in typ or item.get("is_error"):
        return bool(QUOTA.search(json.dumps(item)))
    # Do not stop because an ordinary assistant/tool message quotes a quota test fixture.
    return False

def terminate_tree(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, timeout=10,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            proc.kill()
        proc.wait(timeout=5)

def stream_events(pipe, events, rid):
    try:
        for line in iter(pipe.readline, ""):
            # Raw stdout/stderr stays in memory only. Never echo/persist model/tool output.
            if quota_event(line):
                events.put((rid, "quota"))
            try:
                item = json.loads(line)
                if isinstance(item, dict) and item.get("type") in {"turn.completed", "result"}:
                    usage = item.get("usage")
                    if isinstance(usage, dict):
                        safe = {k: v for k, v in usage.items()
                                if k in {"input_tokens", "output_tokens", "cached_input_tokens",
                                         "cache_read_input_tokens", "cache_creation_input_tokens"}
                                and isinstance(v, (int, float))}
                        if safe:
                            events.put((rid, {"usage": safe}))
                if isinstance(item, dict) and item.get("type") == "item.completed":
                    message = item.get("item", {})
                    if (message.get("type") == "agent_message"
                            and message.get("text", "").strip() == "S03_SMOKE_OK"):
                        events.put((rid, {"smoke_ok": True}))
            except (ValueError, TypeError):
                pass
    finally:
        pipe.close()

def append_log(path, event):
    with path.open("a", encoding="utf-8") as f:
        f.write("\n- " + json.dumps(event, ensure_ascii=True) + "\n")

def record(path, item):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")

def collect_questions(result_path, state_path):
    """Transfer only rare, bounded blocking questions; never credentials or raw output."""
    if not result_path.is_file() or result_path.stat().st_size > 65536:
        return 0
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return 0
    if not isinstance(result, dict):
        return 0
    existing = state_path.read_text(encoding="utf-8")
    accepted = []
    questions = result.get("owner_questions", [])
    if not isinstance(questions, list):
        return 0
    for item in questions[:2]:
        if not isinstance(item, dict) or item.get("blocking") is not True:
            continue
        text = re.sub(r"\s+", " ", str(item.get("question", ""))).strip().replace("|", "/")
        if not 5 <= len(text) <= 300 or text in existing:
            continue
        if re.search(r"AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,}|PRIVATE KEY", text):
            continue
        accepted.append(text)
    if accepted:
        with state_path.open("a", encoding="utf-8") as f:
            f.write("\n### Owner questions — worker blockers (batch once daily)\n")
            for text in accepted:
                f.write("- [ ] " + text + "\n")
    return len(accepted)

def make_prompt(task, rid, wt, timeout, smoke, control_root=None):
    template = (SOURCE / "RUN_PROMPT_TEMPLATE.md").read_text(encoding="utf-8")
    return template.format(rid=rid, task_id=task.id, lane=task.lane).strip()

def stop_dispatch(root):
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("Stop target must be the independent repository root")
    runtime = root / "Run-System" / "Runs"
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "stop.request").write_text(utc(), encoding="utf-8")
    write_state(root / "STATE.md", {"Dispatch enabled": "NO",
        "Next action": "Operator requested stop; verify workers ended before resuming"})
    append_log(root / "Run-System" / "RUN_LOG.md",
        {"utc": utc(), "event": "operator_stop_requested"})
    print("Stop requested; product dispatch disabled.")
    return 0

def accept_task(root, task_id, sha, note):
    if (root / "Run-System" / "Runs" / "dispatcher.lock").exists():
        raise ValueError("Stop dispatcher before accepting tasks; serialized control edits only")
    if git(root, "branch", "--show-current") != "main":
        raise ValueError("Acceptance requires main checkout")
    resolved = git(root, "rev-parse", "--verify", sha + "^{commit}")
    git(root, "merge-base", "--is-ancestor", resolved, "main")
    t = next((x for x in read_queue(root / "QUEUE.md") if x.id == task_id), None)
    if not t or t.status != "PARTIAL" or not note:
        raise ValueError("Need PARTIAL task, verified merged SHA and operator check note")
    set_status(root / "QUEUE.md", task_id, "DONE")
    write_state(root / "STATE.md", {"Last merged SHA": resolved,
        "Last verified command/result": "Operator accepted " + task_id + ": " + note,
        "Next action": "Select next dependency-ready task; retain approval gates"})
    append_log(root / "Run-System" / "RUN_LOG.md",
        {"utc": utc(), "event": "operator_accept", "task": task_id, "sha": resolved})
    return 0

def dispatch(args):
    root = args.repo.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("--repo must be an independent Git root")
    read_queue(root / "QUEUE.md")  # Always inspect real controls, even for harmless fixtures.
    state = read_state(root / "STATE.md")
    harmless = args.dry_run or args.smoke
    if not harmless and state.get("dispatch enabled", "").upper() != "YES":
        raise ValueError("Build dispatch disabled in STATE.md; no product task started")
    if not harmless and state.get("quota halt", "NO").upper() != "NO":
        raise ValueError("Quota halt set; operator must verify reset before clearing it")
    config = json.loads((root / "Run-System" / "dispatcher_config.json").read_text(encoding="utf-8"))
    runtime = root / "Run-System" / "Runs"
    runtime.mkdir(parents=True, exist_ok=True)
    lock = runtime / "dispatcher.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError("Dispatcher lock exists. Inspect recorded PID; never run two schedulers.")
    os.write(fd, str(os.getpid()).encode("ascii"))
    os.close(fd)
    session = ("smoke-" if args.smoke else "dry-" if args.dry_run else "build-") + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    session_dir = runtime / session
    session_dir.mkdir()
    qp, sp = root / "QUEUE.md", root / "STATE.md"
    if harmless:
        qp, sp = session_dir / "QUEUE.md", session_dir / "STATE.md"
        fixture = (SOURCE / "tests" / "fixtures" / "QUEUE.md").read_text(encoding="utf-8")
        if args.smoke:
            fixture = "\n".join(x for x in fixture.splitlines() if not x.startswith("| DRY-") or x.startswith("| DRY-C1-A "))
        qp.write_text(fixture + "\n", encoding="utf-8")
        sp.write_text("| Field | Value |\n|---|---|\n| Dispatch enabled | YES |\n| Quota halt | NO |\n", encoding="utf-8")
    log = root / "Run-System" / "RUN_LOG.md"
    if not log.exists():
        log.write_text("# Dispatcher log\n", encoding="utf-8")
    active, events, history = {}, queue.Queue(), []
    started, peak, halt = 0, 0, None
    worktree_root = Path(config.get("worktrees_root", root / ".worktrees")).resolve()
    if worktree_root != (root / ".worktrees").resolve():
        raise ValueError("Worktrees must live inside this repository's .worktrees")
    stop_file = runtime / "stop.request"
    # Only the process that acquired the dispatcher lock may clear a prior stop request.
    stop_file.unlink(missing_ok=True)
    try:
        while True:
            if stop_file.exists():
                halt = "operator_stop"
            tasks = read_queue(qp)
            read_state(sp)  # Reload operator pause/stop state, never assume it stayed enabled.
            if not harmless and read_state(sp).get("dispatch enabled", "").upper() != "YES":
                halt = "operator_stop"
            while not events.empty():
                _rid, event = events.get_nowait()
                if event == "quota":
                    halt = "quota"
                elif isinstance(event, dict) and _rid in active:
                    active[_rid].update(event)
            for rid, item in list(active.items()):
                proc = item["proc"]
                timed_out = time.monotonic() - item["start"] >= item["timeout"]
                if halt or timed_out:
                    terminate_tree(proc)
                rc = proc.poll()
                if rc is None:
                    continue
                item["watchdog"].cancel()
                for thread in item["threads"]:
                    thread.join(timeout=1)
                while not events.empty():
                    _rid, event = events.get_nowait()
                    if event == "quota":
                        halt = "quota"
                    elif isinstance(event, dict) and _rid in active:
                        active[_rid].update(event)
                status = "quota" if halt == "quota" else "timeout" if timed_out else halt or "exit"
                ok = rc == 0 and not timed_out and not halt
                if harmless and ok:
                    marker = item["worktree"] / ("Run-System/tests/fixtures/MARKER.txt" if args.smoke else item["task"].owns[0])
                    ok = (marker.is_file() and marker.read_text(encoding="utf-8") == MARKER
                          and (not args.smoke or item.get("smoke_ok") is True))
                    if not ok:
                        status = "marker_mismatch"
                task_status = "DONE" if harmless and ok else "PARTIAL"
                set_status(qp, item["task"].id, task_status)
                row = {"utc": utc(), "event": "end", "session": session, "rid": rid,
                       "task": item["task"].id, "lane": item["task"].lane,
                       "model": item["task"].model, "mode": "smoke" if args.smoke else "offline" if args.dry_run else "live",
                       "reason": status, "exit_code": rc, "status": task_status,
                       "elapsed_seconds": round(time.monotonic() - item["start"], 3),
                       "worktree": str(item["worktree"]), "tokens": item.get("usage", "unavailable"),
                       "quota_remaining": "unavailable", "meta_api_spend": "0 for harmless runs; live task must reconcile ledger"}
                history.append(row)
                row["owner_questions_added"] = collect_questions(
                    item["worktree"] / "Run-System" / "Runs" / rid / "RESULT.json", sp)
                append_log(log, row)
                record(session_dir / (rid + ".json"), row)
                del active[rid]
                write_state(sp, {"Last dispatcher run": rid + ": " + task_status,
                    "Last verified command/result": "Child exit " + str(rc) + "; " + status,
                    "Active lanes": ", ".join(x["task"].lane for x in active.values()) or "none",
                    "Next action": "Stop on quota/timeout; otherwise operator verifies PARTIAL worker result before merge/accept"})
                if not ok:
                    halt = halt or status
            if halt:
                if not active:
                    break
                continue
            if not active and args.max_runs and started >= args.max_runs:
                break
            remaining = args.max_runs - started if args.max_runs else 2
            state_now = read_state(sp)
            eligible = read_queue(qp)
            # Keep dependency graph intact while hiding approval-blocked candidates.
            for candidate in eligible:
                if not approval_ready(candidate, state_now):
                    candidate.status = "BLOCKED"
            ready = select_ready(eligible, [x["task"] for x in active.values()], args.max_parallel)
            for task in ready[:remaining]:
                rid = task.id + "-" + uuid.uuid4().hex[:8]
                start = time.monotonic()
                timeout = min(1800, task.minutes * 60, args.timeout_seconds)
                wt = worktree_root / rid
                if wt.exists():
                    raise ValueError("Worktree target already exists; refusing overwrite")
                worktree_root.mkdir(parents=True, exist_ok=True)
                command = build_command(task, config, read_only=args.smoke) if not args.dry_run else [
                    sys.executable, str(SOURCE / "tests" / "harmless_worker.py"),
                    "--target", task.owns[0], "--scenario",
                    args.dry_scenario if task.id == "DRY-C1-A" else "normal"]
                git(root, "worktree", "add", "-b", "run/" + rid, wt, "main")
                manifest = {"rid": rid, "mode": "smoke" if args.smoke else "offline" if args.dry_run else "live",
                    "canonical_root": str(root), "worktree": str(wt), "branch": "run/" + rid,
                    "task": vars(task), "timeout_seconds": timeout,
                    "scope": "S03 harmless verification only; no product code" if harmless else "one authorized queue task"}
                record(wt / "Run-System" / "Runs" / rid / "PLAN.json", manifest)
                prompt = make_prompt(task, rid, wt, timeout, args.smoke, control_root=root)
                (session_dir / (rid + "-PLAN.md")).write_text(
                    f"# {task.id}\n\nLane: {task.lane}\nModel: {task.model}\nOwns: {'; '.join(task.owns)}\nAcceptance: {task.acceptance}\n", encoding="utf-8")
                kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
                proc = subprocess.Popen(command, cwd=wt, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", **kwargs)
                # Independent watchdog: another lane's Git preparation must not delay this deadline.
                watchdog = threading.Timer(max(0, timeout - (time.monotonic() - start)),
                                           terminate_tree, args=(proc,))
                watchdog.daemon = True
                watchdog.start()
                threads = [threading.Thread(target=stream_events, args=(pipe, events, rid), daemon=True)
                           for pipe in (proc.stdout, proc.stderr)]
                for thread in threads:
                    thread.start()
                active[rid] = {"proc": proc, "threads": threads, "start": start,
                    "timeout": timeout, "task": task, "worktree": wt, "watchdog": watchdog}
                proc.stdin.write(prompt)
                proc.stdin.close()
                set_status(qp, task.id, "PARTIAL")  # claimed, never write RUNNING into central queue
                started += 1
                peak = max(peak, len(active))
                append_log(log, {"utc": utc(), "event": "start", "session": session, "rid": rid,
                    "task": task.id, "lane": task.lane, "model": task.model,
                    "command": command, "timeout_seconds": timeout, "worktree": str(wt),
                    "mode": "smoke" if args.smoke else "offline" if args.dry_run else "live"})
                write_state(sp, {"Active lanes": ", ".join(x["task"].lane for x in active.values())})
            if not active:
                break  # human approvals/unmerged results/no dependency-ready tasks: do not spin
            time.sleep(0.05)
        if halt == "quota":
            write_state(sp, {"Quota halt": "YES", "Dispatch enabled": "NO",
                "Active blocker": "quota error; no new dispatch or reroute; operator verifies reset"})
        summary = {"session": session, "mode": "smoke" if args.smoke else "offline" if args.dry_run else "live",
            "started": started, "peak_parallel": peak, "max_parallel": args.max_parallel,
            "halt": halt, "history": history, "root_queue_untouched": harmless,
            "product_files_created": 0 if harmless else "worker-owned changes require review"}
        record(session_dir / "SUMMARY.json", summary)
        print(json.dumps({"session": session, "summary": str(session_dir / "SUMMARY.json"),
            "started": started, "peak_parallel": peak, "halt": halt, "mode": summary["mode"]}))
        return 2 if halt else 0
    finally:
        for item in active.values():
            item["watchdog"].cancel()
            terminate_tree(item["proc"])
            for thread in item["threads"]:
                thread.join(timeout=1)
        # A literal, validated file created by this process, not recursive directory cleanup.
        if lock.parent.resolve() == runtime.resolve() and lock.name == "dispatcher.lock":
            lock.unlink(missing_ok=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=SOURCE.parent)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="offline harmless fixtures; no AI calls")
    mode.add_argument("--smoke", action="store_true", help="one real read-only Sol CLI process on a harmless marker; coding quota only")
    mode.add_argument("--run", action="store_true", help="real queue; STATE Dispatch enabled must be YES")
    mode.add_argument("--stop", action="store_true", help="stop active workers and disable new product dispatch")
    mode.add_argument("--accept", metavar="TASK", help="operator checkpoint after verified FF integration on main")
    parser.add_argument("--merged-sha")
    parser.add_argument("--check-note")
    parser.add_argument("--max-parallel", type=int, choices=[1, 2], default=2)
    parser.add_argument("--max-runs", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--dry-scenario", choices=["normal", "quota", "timeout"], default="normal")
    args = parser.parse_args(argv)
    if not 1 <= args.timeout_seconds <= 1800 or args.max_runs < 0:
        parser.error("timeout must be 1..1800 and max-runs nonnegative")
    if args.smoke:
        args.max_runs = 1
        args.max_parallel = 1
    if not args.dry_run and args.dry_scenario != "normal":
        parser.error("simulated faults are dry-run only")
    try:
        if args.stop:
            return stop_dispatch(args.repo.resolve())
        if args.accept:
            if not args.merged_sha or not args.check_note:
                parser.error("--accept requires --merged-sha and --check-note")
            return accept_task(args.repo.resolve(), args.accept, args.merged_sha, args.check_note)
        return dispatch(args)
    except KeyboardInterrupt:
        print("Stopped by operator; process trees terminated; task worktrees preserved.", file=sys.stderr)
        return 130
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as exc:
        # Never print raw subprocess output; it could contain credentials.
        print("Dispatcher stopped: " + type(exc).__name__ + ": " +
              (str(exc) if isinstance(exc, ValueError) else "inspect sanitized metadata / local configuration"), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
