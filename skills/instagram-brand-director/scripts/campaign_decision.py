#!/usr/bin/env python3
"""Decisive, offline marketing brief triage. No publishing or spending occurs.

Run: python3 -m scripts.campaign_decision examples/campaign-brief.sample.json
All thresholds, formats and objectives are brand policy, not Instagram rules.
"""
import argparse
import json
from datetime import date
from pathlib import Path

from scripts.catalog_guard import assess

GOALS = {"discovery", "community", "conversion", "education"}
FORMATS = {"reel", "carousel", "story"}
PRODUCTION = {"filming_products", "motion_graphics", "static_design", "voiceover", "on_camera"}

def decide(brief, today=None):
    if not isinstance(brief, dict):
        raise ValueError("Brief must be a JSON object.")
    today = today or date.today()
    brand, content, commercial = brief.get("brand"), brief.get("content"), brief.get("commercial", {})
    if not isinstance(brand, dict) or not isinstance(content, dict) or not isinstance(commercial, dict):
        raise ValueError("brand, content and commercial must be objects.")
    goal = content.get("goal")
    if goal not in GOALS:
        return result("REQUEST_CRITICAL_DATA", "Choose a valid campaign objective.", "Confirm discovery, community, conversion or education.", [])
    capabilities = brand.get("production_capabilities", [])
    if not isinstance(capabilities, list) or not set(capabilities).issubset(PRODUCTION):
        raise ValueError("production_capabilities must be a list of supported values.")
    if not capabilities:
        return result("REQUEST_CRITICAL_DATA", "Production capability unknown.", "Identify at least one format the brand can actually produce.", [])
    if content.get("rights_verified") is not True or content.get("claims_verified") is not True:
        return result("HOLD_CREATIVE", "Media rights or claims not yet verified.", "Verify content rights and factual claims before publishing.", [])
    if content.get("requires_face") and "on_camera" not in capabilities:
        return result("REWORK_FACELESS", "Creative requires on-camera presence that the brand cannot provide.",
                      "Rewrite as product footage, graphics or carousel compatible with the brand.", ["on_camera"])
    product_result = None
    if goal == "conversion":
        product = commercial.get("product")
        if not isinstance(product, dict):
            return result("REQUEST_CRITICAL_DATA", "Conversion content requires a specific product record.",
                          "Select a product and verify price, inventory, delivery and sales destination.", [])
        min_margin = commercial.get("minimum_margin_pct", 0)
        if isinstance(min_margin, bool) or not isinstance(min_margin, (float, int)) or not 0 <= min_margin <= 100:
            raise ValueError("minimum_margin_pct must be between 0 and 100")
        product_result = assess(product, purpose="conversion", min_margin_pct=min_margin, today=today)
        if product_result["decision"] != "PROMOTE":
            return result("DO_NOT_PROMOTE", "Commercial preflight failed: " + "; ".join(product_result["blocks"]),
                          "Choose a verified eligible product or produce non-transactional educational content.",
                          [], product_result)
        if product_result["warnings"] and commercial.get("paid_execution_requested"):
            return result("HOLD_PAID_AD", "Paid acquisition requires verified unit economics.",
                          "Confirm unit cost and margin before buying traffic.", [], product_result)
    if commercial.get("paid_execution_requested") and not brand.get("paid_ads_enabled", False):
        return result("PAID_ADS_DISABLED", "Paid-ad execution is an optional module disabled for this brand.",
                      "Use organic content now or explicitly configure paid advertising.", [], product_result)

    preferred = content.get("preferred_format")
    if preferred is not None and preferred not in FORMATS:
        raise ValueError("preferred_format must be reel, carousel or story")
    can_video = bool({"filming_products", "motion_graphics", "on_camera"} & set(capabilities))
    can_static = "static_design" in capabilities
    # A reel can also be built from motion graphics; voice-only without visual production is insufficient.
    if preferred == "reel" and not can_video:
        if can_static:
            return result("CAROUSEL", "Reel production is not feasible with available resources.",
                          "Create a carousel with the same audience promise.", ["reel"], product_result)
        return result("REQUEST_PRODUCTION_CAPABILITY", "No verified production route for the requested Reel.",
                      "Enable product filming, motion graphics or supply static designs.", [], product_result)
    if preferred == "carousel" and not can_static:
        if can_video:
            preferred = "reel"
        else:
            return result("REQUEST_PRODUCTION_CAPABILITY", "Carousel design capability unavailable.",
                          "Identify an achievable creative production method.", [], product_result)
    if preferred == "story" and not can_static and not can_video:
        return result("REQUEST_PRODUCTION_CAPABILITY", "No available Story creation method.",
                      "Provide an achievable visual workflow.", [], product_result)

    chosen = preferred or ("reel" if goal == "discovery" and can_video else "carousel" if can_static else "reel")
    if chosen == "story":
        return result("STORY", "Story selected for the campaign brief.",
                      "Prepare and approve the Story sequence; review replies and qualified actions.", [], product_result)

    if chosen == "carousel":
        return result("CAROUSEL", "Selected format fits brand capability and objective.",
                      "Create and approve a carousel; review saves, shares and qualified conversion actions.", [], product_result)

    if goal == "discovery" and content.get("novel_concept") is True and content.get("time_sensitive") is not True:
        if content.get("trial_available") is True:
            return result("TRIAL_REEL", "Novel discovery content and verified Trial access favor a controlled test.",
                          "Publish as Trial using the native Instagram interface after approval. Review first-party data at ~24h and ~72h.",
                          ["NORMAL_REEL"], product_result)
        if content.get("trial_available") is None:
            return result("VERIFY_TRIAL_ACCESS", "The account's Trial feature availability is unverified.",
                          "Check Trial control in the native app; publish normally if absent.", ["TRIAL_REEL"], product_result)
    return result("NORMAL_REEL", "Immediate reach to current followers, time-sensitive delivery or known creative outweighs Trial testing.",
                  "Produce, review and publish normally after approval; monitor comparable reach, retention, engagement and qualified actions.",
                  ["TRIAL_REEL"], product_result)

def result(decision, why, next_action, rejected, commercial=None):
    return {"decision": decision, "why": why, "next_action": next_action, "rejected_alternatives": rejected,
            "commercial_preflight": commercial, "human_approval_required": True, "executed": False,
            "review_plan": "Define campaign-specific KPIs and review window before publishing.",
            "confidence_note": "This selects a definite action, not a guaranteed Instagram outcome."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("brief")
    args = parser.parse_args()
    data = json.loads(Path(args.brief).read_text(encoding="utf-8"))
    print(json.dumps(decide(data), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
