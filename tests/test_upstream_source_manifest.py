"""Pin provenance of all directly copied third-party files."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "UPSTREAM_SOURCE_MANIFEST.json"

class ProvenanceTests(unittest.TestCase):
    def test_manifest_and_byte_identity(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["files"]), 30)
        for item in data["files"]:
            with self.subTest(path=item["path"]):
                rel = Path(item["path"])
                self.assertFalse(rel.is_absolute())
                self.assertNotIn("..", rel.parts)
                blob = (ROOT / rel).read_bytes()
                actual = hashlib.sha1(f"blob {len(blob)}\0".encode() + blob).hexdigest()
                self.assertEqual(actual, item["upstream_blob_sha"])
                self.assertEqual(actual, item["vendored_blob_sha"])
                self.assertTrue(item["byte_identical"])

    def test_licenses_present(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        prefixes = {x["path"].split("/")[1] for x in data["files"]}
        for prefix in prefixes:
            with self.subTest(vendor=prefix):
                self.assertTrue((ROOT / "third_party" / prefix / "LICENSE").is_file())

if __name__ == "__main__":
    unittest.main()
