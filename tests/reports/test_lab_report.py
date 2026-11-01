import unittest

from Build.reports.lab_report import render


class LabReportTests(unittest.TestCase):
    def test_banner_uses_actual_engine_in_markdown_and_html(self):
        scene = {"gravity": [0, -9.81, 0], "room": {"kind": "floor"}, "objects": []}
        for engine in ("Rapier (same world as the editor Play)", "FALLBACK server RK4 (Rapier failed to load)"):
            with self.subTest(engine=engine):
                report = render(scene, engine, [])
                for key in ("markdown", "html"):
                    self.assertIn(f"server physics run ({engine})", report[key])
                    self.assertIn(f"Engine: {engine}", report[key])
                if engine.startswith("Rapier"):
                    self.assertNotIn("RK4", report["markdown"])
