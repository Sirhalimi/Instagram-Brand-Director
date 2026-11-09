"""Phase 2: deterministic audit of dated source-tagged knowledge, no network."""
import hashlib
import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path
from scripts.knowledge_age import audit, main

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/knowledge-age.sample.md"
SOURCE = ROOT / "knowledge/instagram-rules.md"
INSTALLED = ROOT / "skills/instagram-brand-director/knowledge/instagram-rules.md"

class KnowledgeAgeTests(unittest.TestCase):
    def test_file_header_and_last_segment_dates(self):
        report = audit(FIXTURE.read_text(encoding="utf-8"), today=date(2026, 11, 9))
        self.assertEqual(report["file_verified"], "2026-11-09")
        self.assertEqual(report["entries_checked"], 6)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(len(report["conflicts"]), 2)
        self.assertEqual(len(report["unverified"]), 1)
        self.assertEqual(len(report["undated_entries"]), 2)
        self.assertEqual(len(report["stale_entries"]), 0)

    def test_boundary_exactly_sixty_days_is_not_stale(self):
        example = ("Version: v1 · Verified: 2026-11-09\n"
                   "- A fact · [REPORTED] · source name with 2024 text · 2026-09-10\n")
        report = audit(example, today=date(2026, 11, 9), max_age_days=60)
        self.assertEqual(report["status"], "CURRENT")
        self.assertEqual(report["exit_code"], 0)

    def test_day_sixty_one_is_stale(self):
        example = ("Verified: 2026-11-09\n"
                   "- A fact · [OFFICIAL] · source · 2026-09-09\n")
        report = audit(example, today=date(2026, 11, 9))
        self.assertEqual(report["exit_code"], 1)
        self.assertEqual(report["stale_entries"][0]["age_days"], 61)

    def test_header_stale_even_if_entry_new(self):
        example = ("Verified: 2026-07-01\n"
                   "- New claim · [OFFICIAL] · Meta · 2026-11-09\n")
        result = audit(example, today=date(2026, 11, 9))
        self.assertTrue(result["file_stale"])
        self.assertEqual(result["exit_code"], 1)

    def test_conflicts_are_reported_not_converted_to_stale(self):
        example = ("Verified: 2026-11-09\n"
                   "- Different sources disagree · [CONFLICT] · A vs B · 2026-11-09\n")
        result = audit(example, today=date(2026, 11, 9))
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["exit_code"], 0)

    def test_unverified_undated_entry_is_visible(self):
        example = ("Verified: 2026-11-09\n"
                   "- Unknown access condition · [UNVERIFIED]\n")
        result = audit(example, today=date(2026, 11, 9))
        self.assertEqual(len(result["unverified"]), 1)
        self.assertEqual(len(result["undated_entries"]), 1)
        self.assertEqual(result["exit_code"], 0)

    def test_definition_bullets_are_not_claims(self):
        example = ("Verified: 2026-11-09\n"
                   "## Confidence tags\n"
                   "- **[OFFICIAL]** explanation only\n"
                   "- **[CONFLICT]** definition\n"
                   "## Example claims\n"
                   "- Proper entry · [REPORTED] · news · 2026-11-09\n")
        result = audit(example, today=date(2026, 11, 9))
        self.assertEqual(result["entries_checked"], 1)
        self.assertFalse(result["conflicts"])

    def test_missing_or_invalid_header_fails_closed(self):
        with self.assertRaises(ValueError):
            audit("- A · [OFFICIAL] · Meta · 2026-11-09", today=date(2026,11,9))
        with self.assertRaises(ValueError):
            audit("Verified: 2026-13-01\n",today=date(2026,11,9))

    def test_future_entry_marked_invalid(self):
        example = ("Verified: 2026-11-09\n"
                   "- Future claim · [REPORTED] · source · 2027-02-01\n")
        result = audit(example,today=date(2026,11,9))
        self.assertEqual(result["status"],"INVALID")
        self.assertEqual(result["exit_code"],2)

    def test_cli_reports_nonzero_on_stale_entries(self):
        cmd = [sys.executable, "-m", "scripts.knowledge_age", str(FIXTURE),
               "--as-of", "2027-01-10"]
        res = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                             text=True, check=False, timeout=15)
        self.assertEqual(res.returncode, 1, res.stderr)
        self.assertEqual(json.loads(res.stdout)["status"], "STALE")

    def test_cli_recent_conflict_does_not_block(self):
        cmd=[sys.executable, "-m", "scripts.knowledge_age", str(FIXTURE),
             "--as-of", "2026-11-09"]
        res=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(res.returncode,0)
        self.assertEqual(json.loads(res.stdout)["status"],"REVIEW_REQUIRED")

    def test_user_supplied_knowledge_preserved_in_both_places(self):
        a=SOURCE.read_bytes()
        b=INSTALLED.read_bytes()
        self.assertEqual(a,b)
        manifest=json.loads((ROOT/"knowledge/IMPORT_MANIFEST.json").read_text())
        self.assertEqual(hashlib.sha256(a).hexdigest(),manifest["sha256"])
        self.assertEqual(manifest["source"],"user-provided-library-file")

    def test_actual_source_matches_its_2026_format(self):
        result=audit(SOURCE.read_text(encoding="utf-8"),today=date(2026,11,9))
        self.assertGreaterEqual(result["entries_checked"],20)
        self.assertEqual(result["file_verified"],"2026-11-09")
        self.assertGreaterEqual(len(result["conflicts"]), 3)
        self.assertTrue(result["unverified"])
        self.assertFalse(result["stale_entries"])

if __name__ == "__main__":
    unittest.main()
