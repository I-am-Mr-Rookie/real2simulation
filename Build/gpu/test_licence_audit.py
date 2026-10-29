import tempfile
import unittest
from pathlib import Path

import licence_audit as la


def rec(name, version="1.0", expr=None, lic=None, cls=()):
    return {"name": name, "version": version, "license_expression": expr, "license": lic, "classifiers": list(cls)}


class Classify(unittest.TestCase):
    def test_classes(self):
        cases = {
            "permissive": rec("a", expr="MIT"),
            "denied": rec("b", lic="CC-BY-NC-4.0"),
            "vendor_eula": rec("nvidia-cublas-cu12", cls=["License :: Other/Proprietary License"]),
            "copyleft_review": rec("c", cls=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"]),
            "unknown": rec("d"),
        }
        for want, r in cases.items():
            self.assertEqual(la.classify(r)[0], want, r)
        self.assertEqual(la.classify(rec("e", cls=["License :: OSI Approved :: GNU Lesser General Public "
                                                   "License v3 (LGPLv3)"]))[0], "permissive")
        self.assertEqual(la.classify(rec("f", lic="Proprietary"))[0], "denied")


class Audit(unittest.TestCase):
    def test_pins_drift_and_denial(self):
        lock = Path(tempfile.mkdtemp()) / "lock.txt"
        lock.write_text("# c\nfoo-bar==1.0\n    # via x\nbaz==2.0 ; python_version >= '3'\n"
                        "mapanything @ https://x/zip\n")
        good = [rec("Foo_Bar", "1.0", "MIT"), rec("baz", "2.0", "BSD-3-Clause"), rec("mapanything", "1.1.4", "Apache-2.0")]
        self.assertTrue(la.audit(good, lock)["ok"])
        bad = [rec("foo-bar", "1.1", "MIT"), rec("x", lic="Non-Commercial")]
        errors = la.audit(bad, lock)["errors"]
        self.assertIn("missing pin: baz", errors)
        self.assertIn("version drift: foo-bar: lock 1.0 not in installed ['1.1']", errors)
        self.assertTrue(any(e.startswith("denied licence: x") for e in errors))

    def test_duplicates_and_unreviewed(self):
        lock = Path(tempfile.mkdtemp()) / "lock.txt"
        lock.write_text("foo==1.0\n")
        result = la.audit([rec("foo", "1.0", "MIT"), rec("foo", "0.9", "MIT"), rec("mystery"),
                           rec("mapanything"), rec("plyfile", lic="GNU GENERAL PUBLIC LICENSE Version 3")], lock)
        self.assertEqual(result["duplicates"], {"foo": ["0.9", "1.0"]})
        self.assertEqual(result["errors"], ["unreviewed licence: mystery"])

    def test_real_lock_parses(self):
        pins = la.lock_pins()
        self.assertEqual(pins["torch"], "2.8.0")
        self.assertIn("mapanything", pins)


if __name__ == "__main__":
    unittest.main()
