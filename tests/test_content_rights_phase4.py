"""Phase 4: provenance/rights are checked per source asset, not a single global flag.

All source records are synthetic. These are offline policy-contract tests, not
independent copyright-license checks or evidence of actual Instagram behavior.
"""
import copy
import unittest
from datetime import date
from scripts.campaign_decision import decide, review_source_content

TODAY=date(2026,11,9)

def brief(sources=None,location="top"):
    b={"brand":{"production_capabilities":["filming_products","static_design"],
                "camera_policy":"no"},
       "content":{"goal":"discovery","preferred_format":"reel",
                  "novel_concept":False,"rights_verified":True,
                  "claims_verified":True},
       "commercial":{}}
    if sources is not None:
        if location=="top":
            b["source_content"]=sources
        else:
            b["content"]["source_content"]=sources
    return b

def asset(origin="owned",watermark=False,permission=False,usage="publish",**extra):
    return {"origin":origin,"has_visible_watermark":watermark,
            "documented_permission":permission,"usage":usage,**extra}

class MediaRightsPhase4Tests(unittest.TestCase):
    def test_owned_original_asset_is_eligible_for_manual_review(self):
        out=decide(brief([asset()]),today=TODAY)
        self.assertEqual(out["decision"],"NORMAL_REEL")
        self.assertEqual(out["source_content_review"]["items"][0]["decision"],
                         "ELIGIBLE_FOR_HUMAN_REVIEW")
        self.assertTrue(out["human_approval_required"])
        self.assertFalse(out["executed"])

    def test_no_provenance_does_not_break_legacy_rights_flag(self):
        self.assertEqual(decide(brief(),today=TODAY)["decision"],"NORMAL_REEL")

    def test_unlicensed_third_party_asset_cannot_be_published(self):
        out=decide(brief([asset("third_party")]),today=TODAY)
        self.assertEqual(out["decision"],"HOLD_CREATIVE")
        self.assertEqual(out["source_content_review"]["rejected_publishable_assets"],[0])
        self.assertIn("permission",out["why"].lower()+" "+out["next_action"].lower()+" "+
                        out["source_content_review"]["items"][0]["reason"].lower())

    def test_owned_watermarked_asset_without_documented_permission_is_blocked(self):
        out=decide(brief([asset("owned",watermark=True)]),today=TODAY)
        self.assertEqual(out["decision"],"HOLD_CREATIVE")

    def test_labeled_licensed_or_permission_held_requires_explicit_rights(self):
        for origin in ("licensed","permission"):
            with self.subTest(origin=origin):
                self.assertEqual(decide(brief([asset(origin)]),today=TODAY)["decision"],
                                 "HOLD_CREATIVE")
                self.assertEqual(decide(brief([asset(origin,permission=True)]),today=TODAY)["decision"],
                                 "NORMAL_REEL")

    def test_third_party_with_claimed_permission_still_needs_human_review(self):
        out=decide(brief([asset("third_party",watermark=True,permission=True)]),today=TODAY)
        self.assertEqual(out["decision"],"NORMAL_REEL")
        self.assertTrue(out["source_content_review"]["requires_human_approval"])
        self.assertIn("not independent proof",out["source_content_review"]["items"][0]["reason"])

    def test_research_only_external_source_does_not_enter_publishable_assets(self):
        out=decide(brief([asset("third_party",usage="research"),
                          asset("owned")]),today=TODAY)
        self.assertEqual(out["decision"],"NORMAL_REEL")
        audit=out["source_content_review"]
        self.assertEqual(audit["research_only_indexes"],[0])
        self.assertEqual(audit["items"][0]["decision"],"RESEARCH_ONLY")
        self.assertEqual(audit["rejected_publishable_assets"],[])

    def test_translation_over_other_video_remains_repost_even_with_permission(self):
        out=decide(brief([asset("third_party",permission=True,subtitles_only_repost=True)]),today=TODAY)
        self.assertEqual(out["decision"],"HOLD_CREATIVE")
        self.assertIn("Subtitles",out["source_content_review"]["items"][0]["reason"])

    def test_rejected_asset_list_gives_exact_indexes(self):
        out=decide(brief([asset(),asset("third_party"),asset("owned",watermark=True)]),today=TODAY)
        self.assertEqual(out["source_content_review"]["rejected_publishable_assets"],[1,2])

    def test_compatible_nested_input_source_content(self):
        out=decide(brief([asset("third_party")],location="content"),today=TODAY)
        self.assertEqual(out["decision"],"HOLD_CREATIVE")

    def test_duplicate_source_locations_fail_loudly(self):
        b=brief([asset()])
        b["content"]["source_content"]=[asset()]
        with self.assertRaises(ValueError):
            decide(b,today=TODAY)

    def test_invalid_or_missing_provenance_rejected(self):
        for val in ([{"origin":"third_party","documented_permission":False}],
                    [{"origin":"third_party","documented_permission":"false",
                      "has_visible_watermark":False}],
                    [{"origin":"unknown","documented_permission":True,
                      "has_visible_watermark":False}],
                    [{"origin":"owned","documented_permission":False,
                      "has_visible_watermark":False,"usage":"pubish"}],
                    [{"origin":"owned","documented_permission":False,
                      "has_visible_watermark":False,"subtitles_only_repost":"false"}],
                    [None],"a source string"):
            with self.subTest(val=val):
                with self.assertRaises(ValueError):
                    decide(brief(val if val is not None else [None]),today=TODAY)

    def test_general_rights_verified_false_still_blocks_even_licensed(self):
        b=brief([asset("licensed",permission=True)])
        b["content"]["rights_verified"]=False
        self.assertEqual(decide(b,today=TODAY)["decision"],"HOLD_CREATIVE")

if __name__=="__main__":
    unittest.main()
