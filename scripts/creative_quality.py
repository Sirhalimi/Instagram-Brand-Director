#!/usr/bin/env python3
"""Locale-aware creative lint for Instagram Brand Director.

Uses original, copied Jake Instagram tools for English. Persian text gets
a separate conservative structural review: no unvalidated English hook scores.
This module does not post, use Instagram APIs, or predict engagement.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "third_party" / "jake-instagram-agent-skill" / "skills"
PERSIAN = re.compile(r"[\u0600-\u06ff]")
TOKEN = re.compile(r"[\w\u200c]+", re.UNICODE)
HASHTAG = re.compile(r"(?<!\w)#([\w\u200c]+)", re.UNICODE)
LINK = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
GREETING = re.compile(
    r"^\s*(?:سلام|درود|سلام\s+دوستان|خب\s+بچه(?:ها|‌ها)|دوستان|رفقا)(?:\s|[،!؛:]|$)"
)
PREAMBLE = re.compile(
    r"^\s*(?:(?:توی|در)\s+(?:این\s+)?(?:ویدیو|ویدئو|ریلز)|امروز\s+(?:می‌خواهیم|میخواهیم|می‌خوایم))"
)
CLAIM_PATTERN = re.compile(
    r"(?:صد\s*در\s*صد|۱۰۰\s*[٪%]|100\s*%|تضمین(?:ی)?\s+(?:فروش|درآمد|بازدید))"
)
CTA = {
    "save": re.compile(r"(?:ذخیره\s*کن(?:ید)?|سیو\s*کن(?:ید)?)"),
    "share": re.compile(r"(?:ارسال\s*کن(?:ید)?|بفرست(?:ید)?|به\s+اشتراک\s+بگذار(?:ید)?)"),
    "comment": re.compile(r"(?:کامنت\s+بگذار(?:ید)?|نظر\s+ب(?:ده(?:ید)?|ذار(?:ید)?))"),
    "message": re.compile(r"(?:دایرکت\s+ب(?:ده(?:ید)?|زن(?:ید)?)|پیام\s+ب(?:ده(?:ید)?|فرست(?:ید)?))"),
    "visit": re.compile(r"(?:لینک\s+(?:در\s+)?بیو|وارد\s+سایت\s+شو(?:ید)?)"),
}

def has_persian(text):
    return bool(PERSIAN.search(text))

def words(text):
    return TOKEN.findall(text)

def check_persian_hook(text, policy=None):
    policy = policy or {}
    if not isinstance(text, str) or not text.strip():
        return {"language": "fa", "kind": "hook", "decision": "WRITE_HOOK",
                "issues": ["هوک خالی است."], "notes": [], "metric": {"words": 0},
                "prediction": None, "human_approval_required": True}
    n = len(words(text))
    issues, notes = [], []
    if GREETING.search(text):
        issues.append("شروع با سلام/مقدمه؛ نتیجه یا مسئله مخاطب را جلو بیاور.")
    if PREAMBLE.search(text):
        issues.append("شروع با توضیح درباره خود ویدئو؛ موضوع اصلی را در همان جمله اول بگو.")
    maximum = policy.get("hook_word_soft_max", 16)
    if type(maximum) is not int or maximum < 1 or maximum > 80:
        raise ValueError("hook_word_soft_max must be an integer between 1 and 80")
    if n > maximum:
        issues.append(f"هوک {n} واژه دارد؛ برای خوانایی اولیه کوتاه‌ترش کن (سقف تحریریه: {maximum}).")
    if CLAIM_PATTERN.search(text):
        issues.append("ادعای قطعی یا تضمینی شناسایی شد؛ پیش از استفاده، سند و زمینه ادعا را تأیید کن.")
    if not re.search(r"[\d۰-۹٠-٩]", text):
        notes.append("عدد یا نتیجه مشخص اجباری نیست؛ اگر شواهد واقعی داری، می‌توانی از آن استفاده کنی.")
    return {"language": "fa", "kind": "hook",
            "decision": "REVISE_HOOK" if issues else "READY_FOR_HUMAN_REVIEW",
            "issues": issues, "notes": notes, "metric": {"words": n, "characters": len(text)},
            "prediction": None, "human_approval_required": True,
            "method": "Persian editorial checks; not a reach-prediction score"}

def check_persian_caption(text, policy=None):
    policy = policy or {}
    if not isinstance(text, str) or not text.strip():
        return {"language": "fa", "kind": "caption", "decision": "WRITE_CAPTION",
                "issues": ["کپشن خالی است."], "notes": [], "metric": {"characters": 0, "hashtags": 0},
                "prediction": None, "human_approval_required": True}
    max_chars = policy.get("caption_char_max", 2200)
    max_tags = policy.get("hashtag_policy_max", 5)
    if type(max_chars) is not int or not 1 <= max_chars <= 10000:
        raise ValueError("caption_char_max must be integer between 1 and 10000")
    if type(max_tags) is not int or not 0 <= max_tags <= 30:
        raise ValueError("hashtag_policy_max must be integer between 0 and 30")
    tags = HASHTAG.findall(text)
    issues, notes = [], []
    if len(text) > max_chars:
        issues.append(f"طول کپشن {len(text)} کاراکتر است؛ حد تنظیم‌شده {max_chars} است.")
    if len(tags) > max_tags:
        issues.append(f"تعداد هشتگ‌ها {len(tags)} است؛ سیاست فعلی برند حداکثر {max_tags} است.")
    first = next((s.strip() for s in text.splitlines() if s.strip()), "")
    if GREETING.search(first) or PREAMBLE.search(first):
        issues.append("خط اول با مقدمه عمومی شروع شده؛ پیام اصلی را جلو بیاور.")
    if LINK.search(text):
        notes.append("URL در کپشن عادی اینستاگرام لینک قابل کلیک نیست؛ مسیر معتبر خرید را مشخص کن.")
    if CLAIM_PATTERN.search(text):
        issues.append("ادعای تضمینی نیازمند تأیید مستند است.")
    asks = [key for key, pattern in CTA.items() if pattern.search(text)]
    if len(asks) > 1:
        notes.append("چند CTA متفاوت دیده شد؛ اگر هدف واحد است، یک اقدام اصلی انتخاب کن.")
    if not asks:
        notes.append("CTA مشخص پیدا نشد؛ بسته به هدف محتوا ممکن است قابل قبول باشد.")
    return {"language": "fa", "kind": "caption",
            "decision": "REVISE_CAPTION" if issues else "READY_FOR_HUMAN_REVIEW",
            "issues": issues, "notes": notes,
            "metric": {"characters": len(text), "hashtags": len(tags),
                       "hashtag_values": tags, "cta_categories": asks},
            "prediction": None, "human_approval_required": True,
            "method": "Persian editorial checks; max values are configurable brand policies, not live Meta limits"}

def inspect_english(kind, text):
    if kind == "hook":
        path = VENDOR / "ig-reel" / "hookscore.py"
        args = [sys.executable, str(path), "--hook", text, "--json"]
        stdin = None
    elif kind == "caption":
        path = VENDOR / "ig-caption" / "caption.py"
        args = [sys.executable, str(path), "-", "--json"]
        stdin = text
    else:
        raise ValueError("kind must be hook or caption")
    if not path.is_file():
        return {"language": "en", "kind": kind, "decision": "MANUAL_REVIEW",
                "issues": ["Upstream English tool not installed."], "prediction": None}
    cp = subprocess.run(args, input=stdin, capture_output=True,
                        text=True, timeout=12, check=False)
    # A nonzero return often just means the upstream quality heuristic failed.
    if cp.returncode not in (0, 1):
        raise RuntimeError("Upstream lint failed (not an Instagram platform response).")
    try:
        raw = json.loads(cp.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError("Upstream tool returned invalid JSON.") from e
    return {"language": "en", "kind": kind, "decision": "REVIEW_UPSTREAM_LINT",
            "upstream": raw, "upstream_exit": cp.returncode,
            "method": "Original upstream English-only heuristic; not a performance predictor",
            "prediction": None, "human_approval_required": True}

def inspect(kind, text, policy=None):
    if kind not in ("hook", "caption"):
        raise ValueError("kind must be hook or caption")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if has_persian(text):
        return check_persian_hook(text, policy) if kind == "hook" else check_persian_caption(text, policy)
    if not text.strip():
        return check_persian_hook(text, policy) if kind == "hook" else check_persian_caption(text, policy)
    return inspect_english(kind, text)

def main():
    p = argparse.ArgumentParser(description="Locale-aware creative lint; never posts content")
    p.add_argument("kind", choices=["hook", "caption"])
    text_group = p.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Creative text")
    text_group.add_argument("--file", type=Path, help="Read creative text from a UTF-8 file")
    p.add_argument("--policy", type=Path, help="Optional JSON of editorial policy thresholds")
    args = p.parse_args()
    text = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
    policy = json.loads(args.policy.read_text(encoding="utf-8")) if args.policy else None
    print(json.dumps(inspect(args.kind, text, policy), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
