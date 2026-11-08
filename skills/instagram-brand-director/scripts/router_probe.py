#!/usr/bin/env python3
"""Deterministic route-budget regression probe, not an LLM or a semantic router.

Actual agent follows SKILL.md. Probe measures whether common representative
phrases map to at most one primary and one secondary module.
"""
import argparse, json, re

MAP = [
    ("06-trial-decisions.md",r"trial\b|trial reel|ریلز آزمایشی|ریلز تریال|تست آزمایشی ریل"),
    ("11-commerce-funnel.md",r"out of stock|sold out|ناموجود|تمام شده|موجودی|stock|inventory|حاشیه سود|margin"),
    ("07-content-writing.md",r"caption|کپشن|کاروسل|carousel|استوری|story|پست متنی"),
    ("05-reels.md",r"\breel\b|reels\b|ریلز|هوک|hook\b|storyboard|سناریو ریل"),
    ("01-onboarding.md",r"onboard|brand profile|شناخت برند|معرفی برند|برندمو|هویت برند|جلوی دوربین"),
    ("02-account-audit.md",r"insights|reach drop|audit account|بازدید پیج|افت ریچ|آنالیز پیج"),
    ("03-competitive-intelligence.md",r"competitor|trend|رقبا|رقیب|ترند"),
    ("12-ads-optional.md",r"paid ad|advertising|influencer|تبلیغات پولی|اینفلوئنسر"),
    ("09-organic-seo.md",r"organic growth|instagram seo|سئو اینستاگرام|رشد ارگانیک"),
    ("10-community.md",r"\bdm\b|comment reply|دایرکت|پاسخ کامنت|مدیریت کامنت"),
    ("13-publishing.md",r"publish|schedule|انتشار|زمان‌بندی انتشار|پست کن"),
    ("14-analytics.md",r"analytics|experiment|learn from|گزارش عملکرد|آزمایش محتوا|یادگیری"),
    ("15-governance.md",r"meta policy|instagram rules|قوانین اینستاگرام|قوانین متا|الگوریتم رسمی"),
    ("04-strategy-calendar.md",r"strategy|content plan|calendar|استراتژی|تقویم محتوا|برنامه محتوا"),
    ("08-media-optional.md",r"generate video|generate images|تولید ویدئو با هوش|تولید عکس"),
]
PREFIX="modules/"

def route(prompt, brand=None):
    if not isinstance(prompt,str) or not prompt.strip():
        raise ValueError("prompt cannot be empty")
    brand=brand or {}
    matches=[(name,pattern) for name,pattern in MAP if re.search(pattern,prompt,re.I)]
    primary=matches[0][0] if matches else "04-strategy-calendar.md"
    # Avoid opening production module for a sales offer whose stock is unknown/unavailable.
    extra=[]
    if primary=="05-reels.md" and re.search("product|محصول|فروش",prompt,re.I):
        extra=["11-commerce-funnel.md"]
    if primary=="07-content-writing.md" and re.search("محصول ناموجود|out.of.stock",prompt,re.I):
        primary="11-commerce-funnel.md"
        extra=[]
    # Knowledge is loaded only when the request requires actual Meta policy claims.
    policy=bool(re.search("meta policy|instagram rules|قوانین اینستاگرام|قوانین متا|الگوریتم رسمی",prompt,re.I))
    paths=["SKILL.md",PREFIX+primary]+[PREFIX+x for x in extra]
    if policy and primary!="15-governance.md":
        paths.append("knowledge/instagram-rules.md")
    camera=brand.get("camera_policy","unknown")
    ask_camera=primary=="05-reels.md" and camera=="unknown"
    mode=("production" if primary in ("05-reels.md","07-content-writing.md")
          and not re.search("strategy|استراتژی|آمار|نتایج|تحلیل",prompt,re.I) else "strategy")
    return {"primary":primary,"files":paths,"file_count":len(paths),
            "needs_camera_confirmation":ask_camera,"response_mode":mode,
            "module_count":1+len(extra),"max_files":4}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--camera",choices=["yes","no","unknown"],default="unknown")
    a=ap.parse_args()
    print(json.dumps(route(a.prompt,{"camera_policy":a.camera}),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
