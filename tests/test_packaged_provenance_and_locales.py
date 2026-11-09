"""Regression on installed package provenance, locale extensibility and release status."""
import hashlib, json, re, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills"/"instagram-brand-director"

class ProvenanceAndLocales(unittest.TestCase):
    def test_packaged_upstream_exact_bytes_and_source_commits(self):
        data=json.loads((SKILL/"references/source-attribution.json").read_text(encoding="utf8"))
        self.assertGreaterEqual(len(data["sources"]),20)
        for item in data["sources"]:
            with self.subTest(item=item["path"]):
                blob=(SKILL/item["path"]).read_bytes()
                sha=hashlib.sha1(f"blob {len(blob)}\0".encode()+blob).hexdigest()
                self.assertEqual(sha,item["upstream_blob_sha"])
                self.assertRegex(item["source_commit_sha"],r"^[a-f0-9]{40}$")
                self.assertRegex(item["imported_on"],r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue(item["byte_identical"])

    def test_bilingual_locale_registry(self):
        registry=json.loads((SKILL/"locales/registry.json").read_text(encoding="utf8"))
        self.assertEqual(set(registry["locales"]),{"fa","en"})
        for name,lang in registry["locales"].items():
            self.assertEqual(lang["status"],"supported")
            self.assertTrue((SKILL/"locales"/lang["file"]).is_file())

    def test_release_declares_missing_connectors(self):
        s=json.loads((SKILL/"references/implementation-status.json").read_text(encoding="utf8"))
        self.assertEqual(s["release"],"0.8.0-dev-eval1")
        self.assertEqual(s["capabilities"]["schema_validation"],"implemented")
        self.assertEqual(s["capabilities"]["versioned_behavior_fixtures"],"implemented")
        for missing in ("live_insights_sync","instagram_publish","paid_ads_execution","agent_runtime_eval","additional_languages"):
            self.assertEqual(s["capabilities"][missing],"not-implemented")
        self.assertFalse(s["feature_flags"]["paid_ad_execution_enabled"])
        self.assertFalse(s["feature_flags"]["media_generation_enabled"])

    def test_openai_skill_display_metadata_is_packaged(self):
        content=(SKILL/"agents/openai.yaml").read_text(encoding="utf8")
        self.assertIn('display_name: "Instagram Brand Director"',content)
        self.assertIn("$instagram-brand-director",content)
        self.assertIn('short_description:',content)

    def test_root_has_single_intended_skill(self):
        self.assertFalse((ROOT/"SKILL.md").exists())
        self.assertTrue((SKILL/"SKILL.md").exists())
        self.assertEqual(len(list((SKILL/"modules").glob("*.md"))),16)

if __name__=="__main__":unittest.main()
