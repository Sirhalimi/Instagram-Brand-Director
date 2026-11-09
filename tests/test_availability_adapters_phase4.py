"""Phase 4: supply availability can mean physical, digital, cohort or slots."""
import copy
import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path
from scripts.catalog_guard import assess, analyze
from scripts.campaign_decision import decide

TODAY=date(2026,11,9)
ROOT=Path(__file__).resolve().parents[1]

def base(kind):
    item={"sku":"SYNTHETIC-1","name":"Demo only","availability_type":kind,
          "status":"active","price":"120","unit_cost":"60","currency":"USD",
          "last_verified":"2026-11-09","product_url":"https://example.org/demo"}
    if kind=="digital_product":
        item.update(delivery_mode="automatic",delivery_verified=True,
                    automation_operational=True,license_valid=True,
                    license_valid_until="2027-01-01")
    if kind=="cohort_seats":
        item.update(seats_left=12,start_date="2026-12-01",
                    enrollment_open=True,cohort_confirmed=True)
    if kind=="consult_slots":
        item.update(open_slots=3,slots_verified=True,response_time_hours=24,
                    response_sla_hours=48,service_delivery_verified=True)
    return item

class AvailabilityAdaptersTests(unittest.TestCase):
    def test_legacy_physical_stock_and_explicit_type_are_identical(self):
        old={"sku":"P","name":"Demo","status":"active","currency":"USD",
             "stock_policy":"tracked","stock":10,"price":"100","unit_cost":"60",
             "fulfillment":"automatic","last_verified":"2026-11-09",
             "product_url":"https://example.org/p"}
        alt={**old,"availability_type":"physical_stock"}
        self.assertEqual(assess(old,today=TODAY),assess(alt,today=TODAY))

    def test_each_available_kind_can_pass_offline_guards(self):
        for kind in ("digital_product","cohort_seats","consult_slots"):
            with self.subTest(kind=kind):
                r=assess(base(kind),today=TODAY)
                self.assertEqual(r["decision"],"PROMOTE",r)
                self.assertEqual(r["availability_type"],kind)
                self.assertTrue(r["requires_human_approval"])

    def test_digital_license_missing_or_expired_blocks_new_sales(self):
        for patch in ({"license_valid":False},
                      {"license_valid_until":"2026-11-08"},
                      {"license_valid_until":"not-a-date"}):
            with self.subTest(patch=patch):
                self.assertEqual(assess({**base("digital_product"),**patch},
                                        today=TODAY)["decision"],"DO_NOT_PROMOTE")

    def test_digital_automation_claim_without_operational_check_blocks(self):
        d=base("digital_product")
        d["automation_operational"]=False
        self.assertEqual(assess(d,today=TODAY)["decision"],"DO_NOT_PROMOTE")

    def test_digital_manual_capacity_can_replace_automation(self):
        d=base("digital_product")
        d.update(delivery_mode="manual",manual_capacity_verified=True)
        d.pop("automation_operational")
        self.assertEqual(assess(d,today=TODAY)["decision"],"PROMOTE")
        d["manual_capacity_verified"]=False
        self.assertEqual(assess(d,today=TODAY)["decision"],"DO_NOT_PROMOTE")

    def test_digital_supplier_requires_both_checks(self):
        d=base("digital_product")
        d.update(delivery_mode="supplier",supplier_verified=True,
                 supplier_fulfillment_verified=True)
        self.assertEqual(assess(d,today=TODAY)["decision"],"PROMOTE")
        d["supplier_fulfillment_verified"]=False
        self.assertEqual(assess(d,today=TODAY)["decision"],"DO_NOT_PROMOTE")

    def test_region_restricted_digital_product_requires_verified_restrictions(self):
        d=base("digital_product")
        d["requires_region_check"]=True
        self.assertEqual(assess(d,today=TODAY)["decision"],"DO_NOT_PROMOTE")
        d["region_restrictions_verified"]=True
        self.assertEqual(assess(d,today=TODAY)["decision"],"PROMOTE")

    def test_cohort_sold_out_or_started_returns_do_not_promote(self):
        for patch in ({"seats_left":0},
                      {"start_date":"2026-11-09"},
                      {"start_date":"2026-11-08"},
                      {"enrollment_open":False},
                      {"cohort_confirmed":False},
                      {"enrollment_deadline":"2026-11-08"}):
            with self.subTest(patch=patch):
                self.assertEqual(assess({**base("cohort_seats"),**patch},
                                        today=TODAY)["decision"],"DO_NOT_PROMOTE")

    def test_consult_no_slots_or_unverified_calendar_or_sla_fails(self):
        for patch in ({"open_slots":0},
                      {"open_slots":-1},
                      {"slots_verified":False},
                      {"response_time_hours":None},
                      {"response_time_hours":72},
                      {"service_delivery_verified":False}):
            with self.subTest(patch=patch):
                self.assertEqual(assess({**base("consult_slots"),**patch},
                                        today=TODAY)["decision"],"DO_NOT_PROMOTE")

    def test_unknown_availability_type_fails_closed(self):
        d=base("consult_slots")
        d["availability_type"]="future_unknown_adapter"
        result=assess(d,today=TODAY)
        self.assertEqual(result["decision"],"DO_NOT_PROMOTE")
        self.assertIn("unknown",result["reason"].lower())

    def test_stale_quote_unknown_cost_and_below_margin_are_blocked(self):
        for kind in ("digital_product","cohort_seats","consult_slots"):
            for patch in ({"last_verified":"2026-10-01"},
                          {"unit_cost":None},
                          {"unit_cost":"111"}):
                with self.subTest(kind=kind,patch=patch):
                    r=assess({**base(kind),**patch},today=TODAY,min_margin_pct=20)
                    self.assertEqual(r["decision"],"DO_NOT_PROMOTE")

    def test_sold_out_offer_blocks_conversion_campaign(self):
        for kind,key in (("cohort_seats","seats_left"),
                         ("consult_slots","open_slots")):
            with self.subTest(kind=kind):
                d=base(kind);d[key]=0
                brief={"brand":{"production_capabilities":["static_design"]},
                       "content":{"goal":"conversion","preferred_format":"carousel",
                                  "rights_verified":True,"claims_verified":True},
                       "commercial":{"product":d}}
                out=decide(brief,today=TODAY)
                self.assertEqual(out["decision"],"DO_NOT_PROMOTE")
                self.assertEqual(out["commercial_preflight"]["availability_type"],kind)

    def test_mixed_catalog_analyze_preserves_distinct_adapters(self):
        rows=[]
        for idx,kind in enumerate(("digital_product","cohort_seats","consult_slots")):
            d=base(kind);d["sku"]=f"DEM-{idx}";rows.append(d)
        rows[1]["seats_left"]=0
        out=analyze({"products":rows},today=TODAY)
        self.assertEqual(out["products_reviewed"],3)
        self.assertEqual(out["promotable"],2)
        self.assertEqual(out["results"][1]["decision"],"DO_NOT_PROMOTE")

    def test_cli_reports_synthetic_availability_examples(self):
        cp=subprocess.run([sys.executable,"-m","scripts.catalog_guard",
            str(ROOT/"examples/catalog-availability.phase4.sample.json")],
            cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(cp.returncode,0,cp.stderr)
        j=json.loads(cp.stdout)
        self.assertEqual(j["products_reviewed"],4)
        self.assertEqual(j["promotable"],3)
        self.assertEqual(j["results"][3]["decision"],"DO_NOT_PROMOTE")

if __name__=="__main__":
    unittest.main()
