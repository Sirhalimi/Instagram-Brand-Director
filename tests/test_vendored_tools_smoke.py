"""Smoke test copied unmodified upstream command-line tools.

Do not treat these English-oriented heuristics as Persian content QA.
"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
JAKE=ROOT/"third_party"/"jake-instagram-agent-skill"/"skills"

def run_tool(path, args, input_text=None):
    return subprocess.run([sys.executable,str(JAKE/path),*args], input=input_text,
                          capture_output=True,text=True,encoding="utf-8",timeout=20)

class VendoredToolsSmoke(unittest.TestCase):
    def test_upstream_license_included(self):
        for folder in ("jake-instagram-agent-skill","social-media-skills","sergebulaev-instagram-skills","vidual-digital-marketing-skills"):
            self.assertIn("MIT License",(ROOT/"third_party"/folder/"LICENSE").read_text(encoding="utf-8"))

    def test_hooks_json_parses(self):
        data=json.loads((JAKE/"ig-reel"/"hooks.json").read_text(encoding="utf-8"))
        self.assertTrue(data.get("hooks"))

    def test_hookscore_cli(self):
        result=run_tool(Path("ig-reel/hookscore.py"),["--hook","I saved $240 on one mistake.","--json"])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIsInstance(json.loads(result.stdout),dict)

    def test_beats_cli(self):
        result=run_tool(Path("ig-reel/beats.py"),["-","--json"],input_text="I saved $240.\nHere is why.\n")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertGreater(json.loads(result.stdout)["total_seconds"],0)

    def test_caption_cli(self):
        result=run_tool(Path("ig-caption/caption.py"),["-","--json"],input_text="Save this guide for your next product launch.")
        self.assertIn(result.returncode,(0,1),result.stderr)
        self.assertIn("verdict",json.loads(result.stdout))

    def test_viral_swipe_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"reels.tsv"
            p.write_text("account\tfollowers\tmedian\tviews\thook\n@sample\t1000\t400\t2200\tI saved $240\n",encoding="utf-8")
            result=run_tool(Path("ig-viral/swipe.py"),[str(p),"--json"])
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)["n"],1)

if __name__=="__main__":
    unittest.main()
