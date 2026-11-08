"""The CLI-installed Skill must run exactly the code passing root regression tests."""
import hashlib
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills"/"instagram-brand-director"
FILES=("campaign_decision.py","catalog_guard.py","trial_review.py","creative_quality.py")

class RuntimeConsistencyTests(unittest.TestCase):
    def test_no_shadow_copy_divergence(self):
        for name in FILES:
            with self.subTest(name=name):
                root=(ROOT/"scripts"/name).read_bytes()
                installed=(SKILL/"scripts"/name).read_bytes()
                self.assertEqual(hashlib.sha256(root).hexdigest(),hashlib.sha256(installed).hexdigest(),
                    "Root tests and installed Skill have diverged; update both or remove the duplicate")
    def test_baseline_and_learning_guards_shipped(self):
        for name in ("baseline_builder.py","validate_data.py","learning_gate.py"):
            with self.subTest(name=name):
                self.assertTrue((SKILL/"scripts"/name).is_file())

if __name__=="__main__":unittest.main()
