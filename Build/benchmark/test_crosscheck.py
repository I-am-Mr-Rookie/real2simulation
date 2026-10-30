import json, shutil, subprocess, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import about, crosscheck as cc
import manifest as mf


class CrossCheckTest(unittest.TestCase):
    def test_committed_pitch_numbers_match_evidence(self):
        res = cc.check()
        self.assertEqual(res["mismatches"], [])
        self.assertGreater(res["checked"], 60)

    def test_authored_or_drifted_numbers_fail(self):
        md = cc.MD.read_text(encoding="utf-8")
        for bad in (md.replace("| 0.1982 |", "| 0.2000 |"),                 # table drift
                    md + "\nThe fitter is 0.987 accurate.\n",                 # authored prose number
                    md.replace("8 measured, 8 UNAVAILABLE", "9 measured, 7 UNAVAILABLE"),
                    md.replace("7 of 466 sealed", "9 of 466 sealed"),
                    md.replace("Gate A **MET_AMENDED_Q16**", "Gate A **MET**")):
            self.assertNotEqual(bad, md)
            self.assertEqual(cc.check(md_text=bad)["status"], "FAIL")

    def test_about_and_jsx_tamper_fail(self):
        ab = json.loads(about.OUT.read_text(encoding="utf-8"))
        ab["sections"]["costs"]["rows"][0]["value"] = 1.0
        self.assertEqual(cc.check(about_doc=ab)["status"], "FAIL")
        jsx = cc.JSX.read_text(encoding="utf-8").replace("Gate RS:", "Gate RS (0.19):")
        self.assertEqual(cc.check(jsx_text=jsx)["status"], "FAIL")

    def test_about_jsx_compiles(self):
        # node_modules live in the main checkout; a worktree sits at <main>/.worktrees/<id>
        web = next((r / "Build/web" for r in (mf.ROOT, mf.ROOT.parent.parent)
                    if (r / "Build/web/node_modules/next").is_dir()), None)
        if web is None or not shutil.which("node"):
            self.skipTest("node or Build/web/node_modules/next unavailable")
        out = subprocess.run(["node", str(Path(__file__).with_name("jsx_check.cjs")), str(web), str(cc.JSX)],
                             capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)


if __name__ == "__main__":
    unittest.main()
