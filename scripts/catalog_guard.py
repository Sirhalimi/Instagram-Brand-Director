#!/usr/bin/env python3
"""Offline product catalog guardrail. No account, store or supplier writes."""
import argparse
import json
from datetime import date
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path

VALID_STATUS = {"active", "draft", "archived", "paused"}

def money(value):
    try:
        result = Decimal(str(value)) if value is not None else None
        return result if result is None or result.is_finite() else None
    except (InvalidOperation, ValueError, TypeError):
        return None

def assess(product, purpose="conversion", min_margin_pct=0, today=None, max_age_days=14):
    if not isinstance(product, dict):
        raise ValueError("Product must be an object.")
    if purpose not in ("conversion", "promotion", "awareness"):
        raise ValueError("Unrecognized promotion purpose.")
    if type(min_margin_pct) not in (int, float) or not math.isfinite(min_margin_pct) or not 0 <= min_margin_pct <= 100:
        raise ValueError("Margin floor must be a finite percentage between 0 and 100.")
    if type(max_age_days) is not int or max_age_days < 0:
        raise ValueError("Maximum data age must be a nonnegative integer.")
    today = today or date.today()
    blocks, warnings, missing = [], [], []
    for field in ("sku", "name", "status", "currency", "fulfillment", "last_verified", "price", "unit_cost", "stock_policy"):
        if product.get(field) in (None, ""):
            missing.append(field)
    if not isinstance(product.get("currency"), str) or not product["currency"].strip():
        blocks.append("Currency unknown; cannot quote a reliable sale price.")
    if product.get("fulfillment") not in ("automatic", "manual", "supplier"):
        blocks.append("Fulfillment model unknown.")
    if product.get("status") not in VALID_STATUS:
        blocks.append("Product status is absent or unrecognized.")
    elif product["status"] != "active":
        blocks.append("Product is not active for new sales.")
    policy, stock = product.get("stock_policy"), product.get("stock")
    if policy == "tracked":
        if type(stock) is not int or stock < 0:
            blocks.append("Tracked stock count must be a nonnegative integer.")
        elif stock == 0:
            blocks.append("Product is out of stock.")
    elif policy == "supplier":
        if product.get("supplier_verified") is not True:
            blocks.append("Supplier availability is unverified.")
    elif policy == "unlimited":
        if product.get("unlimited_verified") is not True:
            blocks.append("Unlimited supply assertion needs verification.")
    else:
        blocks.append("Stock policy is unknown.")
    price, cost = money(product.get("price")), money(product.get("unit_cost"))
    margin_pct = None
    if price is None or price <= 0:
        blocks.append("Sale price is missing or invalid.")
    if cost is None or cost < 0:
        if purpose in ("promotion", "conversion"):
            blocks.append("Cost unknown; margin cannot be verified for a new-sales promotion.")
        else:
            warnings.append("Cost/margin unknown; avoid purchase claims until verified.")
    elif price is not None and price > 0:
        margin_pct = float((price - cost) / price * 100)
        if margin_pct < float(min_margin_pct):
            blocks.append("Gross margin below configured campaign floor.")
    if product.get("fulfillment") in ("manual", "supplier") and not product.get("fulfillment_capacity_verified", False):
        blocks.append("Manual/supplier delivery capacity not verified.")
    stamp = product.get("last_verified")
    if stamp:
        try:
            age = (today - date.fromisoformat(stamp)).days
            if age < 0:
                blocks.append("Verification date is in the future.")
            if age > max_age_days:
                blocks.append("Price/stock verification is stale.")
        except (ValueError, TypeError):
            blocks.append("Invalid verification date.")
    else:
        blocks.append("Verification timestamp missing.")
    if purpose in ("conversion", "promotion") and not product.get("product_url"):
        blocks.append("Sales destination not verified.")
    if product.get("restricted_claims"):
        blocks.append("Restricted/unverified product claims require review.")
    return {"sku": product.get("sku"), "name": product.get("name"),
            "decision": "PROMOTE" if not blocks else "DO_NOT_PROMOTE",
            "reason": blocks[0] if blocks else "Commercial preflight passed.",
            "blocks": blocks, "warnings": warnings, "missing_fields": missing,
            "gross_margin_pct": margin_pct, "requires_human_approval": True}

def analyze(catalog, **kwargs):
    products = catalog.get("products")
    if not isinstance(products, list):
        raise ValueError("Catalog needs products array.")
    seen, results = set(), []
    for product in products:
        if not isinstance(product, dict):
            raise ValueError("Each product must be an object.")
        sku = product.get("sku")
        if not sku or sku in seen:
            raise ValueError("Product SKU required and unique.")
        seen.add(sku)
        results.append(assess(product, **kwargs))
    return {"products_reviewed": len(results),
            "promotable": sum(x["decision"] == "PROMOTE" for x in results),
            "results": results}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog")
    parser.add_argument("--purpose", choices=["conversion", "promotion", "awareness"], default="conversion")
    parser.add_argument("--min-margin-pct", type=float, default=0)
    args = parser.parse_args()
    data = json.loads(Path(args.catalog).read_text(encoding="utf8"))
    print(json.dumps(analyze(data, purpose=args.purpose,
                             min_margin_pct=args.min_margin_pct), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
