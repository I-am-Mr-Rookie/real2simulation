"""Deterministic dispatcher checks. All integration workers are harmless Python fixtures."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatcher as d

SOURCE = Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent

class SchedulerTests(unittest.TestCase):
    def task(self, id="A", lane="CODEX-1", depends=None, owns=None, status="TODO"):
        return d.Task(id, lane, "GPT-6.1 Sol / medium", "P"+id, 30,
                      "Harmless", depends or [], owns or [id+"/"], "check", status)

    def test_two_max_and_one_per_lane(self):
        tasks = [self.task("A"), self.task("B"), self.task("C", "CODEX-2"),
                 self.task("D", "CLAUDE")]
        self.assertEqual([x.id for x in d.select_ready(tasks, [])], ["A", "C"])
        self.assertEqual(d.select_ready(tasks, tasks[:1])[0].id, "C")
        with self.assertRaises(ValueError):
            d.select_ready(tasks, [], 3)

    def test_dependencies_and_human_lane(self):
        a = self.task("A", status="PARTIAL")
        b = self.task("B", "CODEX-2", ["A"])
        human = self.task("H", "KOUSHIK")
        self.assertEqual(d.select_ready([a,b,human], []), [])
        a.status = "DONE"
        self.assertEqual([x.id for x in d.select_ready([a,b,human], [])], ["B"])

    def test_parent_dependency_includes_review(self):
        a, review = self.task("A", status="DONE"), self.task("R", "CLAUDE")
        a.step = review.step = "S01"
        b = self.task("B", "CODEX-2", ["S01"])
        self.assertEqual(d.select_ready([a,review,b], [review]), [])
        review.status = "DONE"
        self.assertEqual([x.id for x in d.select_ready([a,review,b], [])], ["B"])

    def test_cross_lane_paths(self):
        a = self.task("A", owns=["shared/"])
        b = self.task("B", "CODEX-2", owns=["shared/file.txt"])
        self.assertTrue(d.overlap(a,b))
        self.assertEqual([x.id for x in d.select_ready([a,b], [])], ["A"])

    def test_cycles_and_unknown_deps_rejected(self):
        with self.assertRaises(ValueError):
            d.validate_dependencies([self.task("A",depends=["B"]),self.task("B",depends=["A"])])
        with self.assertRaises(ValueError):
            d.validate_dependencies([self.task(depends=["missing"])])

    def test_exact_cli_commands_no_bypass_or_resume(self):
        cfg = json.loads((SOURCE/"dispatcher_config.json").read_text(encoding="utf-8"))
        resolve = lambda x: "C:/tools/"+x
        a = d.build_command(self.task(), cfg, resolve)
        self.assertEqual(a[1], "exec")
        self.assertIn("gpt-6.1-sol", a)
        self.assertIn('model_reasoning_effort="medium"', a)
        self.assertEqual(a[a.index("--sandbox")+1], "workspace-write")
        smoke = d.build_command(self.task(), cfg, resolve, read_only=True)
        self.assertEqual(smoke[smoke.index("--sandbox")+1], "read-only")
        c = self.task(lane="CLAUDE")
        c.model = "Haiku 5.5 / high"
        b = d.build_command(c,cfg,resolve)
        self.assertIn("-p", b)
        self.assertIn("claude-haiku-5-5", b)
        self.assertIn("--effort",b)
        self.assertFalse(any("bypass" in x or "resume" == x for x in a+b))
        c.model = "Haiku 5.5 / medium"
        with self.assertRaises(ValueError):
            d.build_command(c,cfg,resolve)

    def test_quota_events_not_quoted_fixture(self):
        self.assertTrue(d.quota_event('{"type":"error","error":{"code":"insufficient_quota"}}'))
        self.assertTrue(d.quota_event('{"type":"error","error":{"status":429}}'))
        self.assertTrue(d.quota_event('{"type":"rate_limit_event","rate_limit_info":{"status":"rejected"}}'))
        self.assertFalse(d.quota_event('{"type":"rate_limit_event","rate_limit_info":{"status":"allowed_warning"}}'))
        self.assertFalse(d.quota_event('{"type":"assistant","text":"test insufficient_quota"}'))

    def test_write_scope_requires_owner_approval_and_rejects_unrestricted(self):
        cfg = json.loads((SOURCE/"dispatcher_config.json").read_text(encoding="utf-8"))
        resolve = lambda x: "C:/tools/"+x
        cfg["codex_workspace_write_approved"] = False
        with self.assertRaises(ValueError):
            d.build_command(self.task(), cfg, resolve)
        cfg["codex_sandbox"] = "danger-full-access"
        cfg["codex_workspace_write_approved"] = True
        with self.assertRaises(ValueError):
            d.build_command(self.task(), cfg, resolve)

    def test_prompt_format(self):
        t=self.task()
        value=d.make_prompt(t,"RID",Path("C:/example"),1800,False)
        self.assertEqual(value, "Complete run RID (task A, lane CODEX-1).")
        self.assertLess(len(value), 120)

    def test_sensitive_actions_need_recorded_approval(self):
        t = self.task("S25e", "CODEX-2")
        t.step = "S25"
        self.assertFalse(d.approval_ready(t, {}))
        self.assertTrue(d.approval_ready(t, {"public repo approval": "YES"}))
        t.id, t.step = "S22c", "S22"
        self.assertFalse(d.approval_ready(t, {"judging candidate approval": "YES"}))
        self.assertTrue(d.approval_ready(t, {"judging candidate approval": "YES",
                                           "fresh qa identities ready": "YES"}))

class ProcessTests(unittest.TestCase):
    def harness(self):
        parent = ROOT/".worktrees"/"verification"/("test-"+uuid.uuid4().hex[:10])
        root = parent/"repo"
        (root/"Run-System").mkdir(parents=True)
        (root/"QUEUE.md").write_text((SOURCE/"tests"/"fixtures"/"QUEUE.md").read_text(encoding="utf-8"),encoding="utf-8")
        (root/"STATE.md").write_text("| Field | Value |\n|---|---|\n| Dispatch enabled | NO |\n| Quota halt | NO |\n",encoding="utf-8")
        config=json.loads((SOURCE/"dispatcher_config.json").read_text(encoding="utf-8"))
        config["repo_root"]=str(root)
        config["worktrees_root"]=str(root/".worktrees")
        (root/"Run-System"/"dispatcher_config.json").write_text(json.dumps(config),encoding="utf-8")
        for argv in [
            ["git","init","-b","main"],
            ["git","add","QUEUE.md","STATE.md","Run-System/dispatcher_config.json"],
            ["git","-c","user.name=S03 Test","-c","user.email=s03-test@example.invalid",
             "commit","-m","test fixture: harmless inputs only"]
        ]:
            subprocess.run(argv,cwd=root,check=True,capture_output=True,timeout=20)
        # Keep fixtures/worktrees for inspection; no recursive deletion on Windows.
        return root

    def run_case(self, mode="normal"):
        root=self.harness()
        before=hashlib.sha256((root/"QUEUE.md").read_bytes()).hexdigest()
        argv=[sys.executable,str(SOURCE/"dispatcher.py"),"--repo",str(root),
              "--dry-run","--dry-scenario",mode]
        if mode=="timeout":
            argv += ["--timeout-seconds","1"]
        p=subprocess.run(argv,capture_output=True,text=True,timeout=30)
        self.assertEqual(p.returncode,0 if mode=="normal" else 2,p.stderr)
        receipt=json.loads(p.stdout.splitlines()[-1])
        summary=json.loads(Path(receipt["summary"]).read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256((root/"QUEUE.md").read_bytes()).hexdigest(),before)
        self.assertLessEqual(summary["peak_parallel"],2)
        self.assertFalse((root/"Run-System"/"Runs"/"dispatcher.lock").exists())
        for item in summary["history"]:
            self.assertTrue(Path(item["worktree"]).is_dir())
            self.assertLess(item["elapsed_seconds"],15)
        return root,summary

    def test_real_worktrees_offline_two_parallel(self):
        root,s=self.run_case()
        self.assertEqual(s["started"],4)
        self.assertEqual(s["peak_parallel"],2)
        self.assertEqual({x["status"] for x in s["history"]},{"DONE"})
        self.assertEqual(len({x["worktree"] for x in s["history"]}),4)
        for item in s["history"]:
            self.assertFalse((Path(item["worktree"])/"Build").exists())

    def test_quota_stops_dispatch_and_marks_halt(self):
        root,s=self.run_case("quota")
        self.assertEqual(s["halt"],"quota")
        self.assertLessEqual(s["started"],2)
        state=d.read_state(root/"Run-System"/"Runs"/s["session"]/"STATE.md")
        self.assertEqual(state["quota halt"],"YES")
        self.assertEqual(state["dispatch enabled"],"NO")

    def test_timeout_kills_real_child_process_tree(self):
        root,s=self.run_case("timeout")
        self.assertEqual(s["halt"],"timeout")
        self.assertTrue(any(x["reason"]=="timeout" for x in s["history"]))

    def test_live_dispatch_disabled(self):
        root=self.harness()
        p=subprocess.run([sys.executable,str(SOURCE/"dispatcher.py"),"--repo",str(root),"--run"],
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,1)
        self.assertIn("disabled",p.stderr)
        self.assertFalse((root/"Run-System"/"RUN_LOG.md").exists())

    def test_stop_command_persists_pause(self):
        root=self.harness()
        p=subprocess.run([sys.executable,str(SOURCE/"dispatcher.py"),"--repo",str(root),"--stop"],
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(d.read_state(root/"STATE.md")["dispatch enabled"],"NO")
        self.assertTrue((root/"Run-System"/"Runs"/"stop.request").is_file())

    def test_stop_command_ends_active_harmless_workers(self):
        root=self.harness()
        flags={"creationflags":subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP} if os.name=="nt" else {"start_new_session":True}
        proc=subprocess.Popen([sys.executable,str(SOURCE/"dispatcher.py"),"--repo",str(root),
                               "--dry-run","--dry-scenario","timeout","--timeout-seconds","15"],
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,**flags)
        try:
            log=root/"Run-System"/"RUN_LOG.md"
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                if log.exists() and '"event": "start"' in log.read_text(encoding="utf-8"):break
                time.sleep(0.05)
            else:self.fail("Harmless worker did not start")
            subprocess.run([sys.executable,str(SOURCE/"dispatcher.py"),"--repo",str(root),"--stop"],
                           check=True,capture_output=True,text=True,timeout=10)
            out,err=proc.communicate(timeout=10)
            self.assertEqual(proc.returncode,2,err)
            self.assertEqual(json.loads(out.splitlines()[-1])["halt"],"operator_stop")
        finally:
            d.terminate_tree(proc)

    def test_owner_questions_only_blockers_and_deduplicated(self):
        root=self.harness()
        result=root/"result.json"
        result.write_text(json.dumps({"owner_questions":[
            {"question":"Approve the scoped verification action?","blocking":True},
            {"question":"Unneeded stylistic preference?","blocking":False}]}),encoding="utf-8")
        self.assertEqual(d.collect_questions(result,root/"STATE.md"),1)
        self.assertEqual(d.collect_questions(result,root/"STATE.md"),0)
        self.assertNotIn("Unneeded stylistic", (root/"STATE.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
