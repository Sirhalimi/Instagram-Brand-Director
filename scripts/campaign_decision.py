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


CONTENT_ORIGINS = {"owned", "licensed", "permission", "third_party"}
ASSET_USAGES = {"publish", "research"}

def review_source_content(records):
    """Audit declared media provenance, without claiming license verification."""
    if records is None:
        return None  # Preserve legacy rights_verified-only briefs.
    if not isinstance(records, list):
        raise ValueError("source_content must be an array.")
    reviewed, rejected, research = [], [], []
    for idx, item in enumerate(records):
        if not isinstance(item, dict):
            raise ValueError("source_content entries must be objects.")
        allowed = {"origin", "has_visible_watermark", "documented_permission",
                   "usage", "subtitles_only_repost"}
        extra = set(item) - allowed
        if extra:
            raise ValueError("Unsupported source_content keys: " + ", ".join(sorted(extra)))
        origin = item.get("origin")
        if origin not in CONTENT_ORIGINS:
            raise ValueError("source_content origin must be owned, licensed, permission or third_party.")
        for field in ("has_visible_watermark", "documented_permission"):
            if type(item.get(field)) is not bool:
                raise ValueError("source_content.%s must be explicitly boolean." % field)
        usage = item.get("usage", "publish")
        if usage not in ASSET_USAGES:
            raise ValueError("source_content.usage must be publish or research.")
        if "subtitles_only_repost" in item and type(item["subtitles_only_repost"]) is not bool:
            raise ValueError("source_content.subtitles_only_repost must be boolean.")
        problems = []
        if item.get("subtitles_only_repost") is True:
            problems.append("Subtitles/translation alone do not make a third-party video original.")
        if origin in ("third_party", "licensed", "permission") and not item["documented_permission"]:
            problems.append("Non-owned asset lacks documented publication permission.")
        if item["has_visible_watermark"] and not item["documented_permission"]:
            problems.append("Watermarked asset lacks documented publication permission.")
        if usage == "research":
            research.append(idx)
            outcome = "RESEARCH_ONLY"
            note = "Hooks/topics/references only; produce new original media instead."
        elif problems:
            rejected.append(idx)
            outcome = "REJECT_PUBLISHABLE_ASSET"
            note = "; ".join(problems)
        else:
            outcome = "ELIGIBLE_FOR_HUMAN_REVIEW"
            note = "Declared permission is not independent proof of rights or Instagram originality."
        reviewed.append({"index": idx, "origin": origin, "usage": usage,
                         "decision": outcome, "reason": note})
    return {"items": reviewed, "rejected_publishable_assets": rejected,
            "research_only_indexes": research, "requires_human_approval": True,
            "note": "No external asset or permission verification occurred."}

def decide(brief, today=None):
    if not isinstance(brief, dict):
        raise ValueError("Brief must be a JSON object.")
    today = today or date.today()
    brand, content, commercial = brief.get("brand"), brief.get("content"), brief.get("commercial", {})
    if not isinstance(brand, dict) or not isinstance(content, dict) or not isinstance(commercial, dict):
        raise ValueError("brand, content and commercial must be objects.")
    if "source_content" in brief and "source_content" in content:
        raise ValueError("Specify source_content once, not at both brief/content levels.")
    source_review = review_source_content(
        brief["source_content"] if "source_content" in brief else content.get("source_content"))
    goal = content.get("goal")
    if goal not in GOALS:
        return result("REQUEST_CRITICAL_DATA", "Choose a valid campaign objective.", "Confirm discovery, community, conversion or education.", [])
    capabilities = brand.get("production_capabilities", [])
    if not isinstance(capabilities, list) or not set(capabilities).issubset(PRODUCTION):
        raise ValueError("production_capabilities must be a list of supported values.")
    if not capabilities:
        return result("REQUEST_CRITICAL_DATA", "Production capability unknown.", "Identify at least one format the brand can actually produce.", [])
    for field in ("rights_verified", "claims_verified", "requires_face", "novel_concept", "time_sensitive", "trial_available"):
        if field in content and content[field] is not None and type(content[field]) is not bool:
            raise ValueError(f"{field} must be a boolean or null.")
    for owner, field in ((brand, "paid_ads_enabled"), (commercial, "paid_execution_requested")):
        if field in owner and type(owner[field]) is not bool:
            raise ValueError(f"{field} must be a boolean.")
    camera_policy = brand.get("camera_policy")
    if camera_policy not in (None, "yes", "no", "unknown"):
        raise ValueError("camera_policy must be yes/no/unknown.")
    if camera_policy == "no" and "on_camera" in capabilities:
        return result("REWORK_FACELESS", "The brand does not permit on-camera production.",
                      "Remove on-camera production from the plan and use faceless capabilities.", ["on_camera"])
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
    if content.get("rights_verified") is not True or content.get("claims_verified") is not True:
        return result("HOLD_CREATIVE", "Media rights or claims not yet verified.", "Verify content rights and factual claims before publishing.", [], product_result, source_review)
    if source_review and source_review["rejected_publishable_assets"]:
        return result("HOLD_CREATIVE", "Unsafe external asset in publishable content: " +
                      ", ".join(str(i) for i in source_review["rejected_publishable_assets"]),
                      "Replace with original production or obtain documented rights and human review. "
                      "Subtitles-only translation is still a repost; research media cannot be published.",
                      [], product_result, source_review)
    if content.get("requires_face") is True and (camera_policy == "no" or "on_camera" not in capabilities):
        return result("REWORK_FACELESS", "Creative requires an on-camera presenter unavailable to this brand.",
                      "Rewrite using product footage, graphics or a carousel.", ["on_camera"], product_result, source_review)
    if commercial.get("paid_execution_requested") and not brand.get("paid_ads_enabled", False):
        return result("PAID_ADS_DISABLED", "Paid-ad execution is an optional module disabled for this brand.",
                      "Use organic content now or explicitly configure paid advertising.", [], product_result, source_review)

    preferred = content.get("preferred_format")
    if preferred is not None and preferred not in FORMATS:
        raise ValueError("preferred_format must be reel, carousel or story")
    can_video = bool({"filming_products", "motion_graphics", "on_camera"} & set(capabilities))
    can_static = "static_design" in capabilities
    # A reel can also be built from motion graphics; voice-only without visual production is insufficient.
    if preferred == "reel" and not can_video:
        if can_static:
            return result("CAROUSEL", "Reel production is not feasible with available resources.",
                          "Create a carousel with the same audience promise.", ["reel"], product_result, source_review)
        return result("REQUEST_PRODUCTION_CAPABILITY", "No verified production route for the requested Reel.",
                      "Enable product filming, motion graphics or supply static designs.", [], product_result, source_review)
    if preferred == "carousel" and not can_static:
        if can_video:
            preferred = "reel"
        else:
            return result("REQUEST_PRODUCTION_CAPABILITY", "Carousel design capability unavailable.",
                          "Identify an achievable creative production method.", [], product_result, source_review)
    if preferred == "story" and not can_static and not can_video:
        return result("REQUEST_PRODUCTION_CAPABILITY", "No available Story creation method.",
                      "Provide an achievable visual workflow.", [], product_result, source_review)

    chosen = preferred or ("reel" if goal == "discovery" and can_video else "carousel" if can_static else "reel")
    if chosen == "story":
        return result("STORY", "Story selected for the campaign brief.",
                      "Prepare and approve the Story sequence; review replies and qualified actions.", [], product_result, source_review)

    if chosen == "carousel":
        return result("CAROUSEL", "Selected format fits brand capability and objective.",
                      "Create and approve a carousel; review saves, shares and qualified conversion actions.", [], product_result, source_review)

    if goal == "discovery" and content.get("novel_concept") is True and content.get("time_sensitive") is not True:
        if content.get("trial_available") is True:
            return result("TRIAL_REEL", "Novel discovery content and verified Trial access favor a controlled test.",
                          "Publish as Trial using the native Instagram interface after approval. Review first-party data at ~24h and ~72h.",
                          ["NORMAL_REEL"], product_result, source_review)
        if content.get("trial_available") is None:
            return result("VERIFY_TRIAL_ACCESS", "The account's Trial feature availability is unverified.",
                          "Check Trial control in the native app; publish normally if absent.", ["TRIAL_REEL"], product_result, source_review)
    return result("NORMAL_REEL", "Immediate reach to current followers, time-sensitive delivery or known creative outweighs Trial testing.",
                  "Produce, review and publish normally after approval; monitor comparable reach, retention, engagement and qualified actions.",
                  ["TRIAL_REEL"], product_result, source_review)

def result(decision, why, next_action, rejected, commercial=None, source_review=None):
    return {"decision": decision, "why": why, "next_action": next_action, "rejected_alternatives": rejected,
            "commercial_preflight": commercial, "source_content_review": source_review,
            "human_approval_required": True, "executed": False,
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
