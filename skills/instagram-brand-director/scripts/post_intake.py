#!/usr/bin/env python3
"""Offline per-post intake; reads only explicitly provided brand/post/answer paths.

The CLI never saves by default. --save explicitly updates only its --brand
Markdown file and selected durable preferences using an atomic same-folder
replacement. No API, credentials or network.
"""
import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("_igbd_validator", DIR / "validate_data.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
GOALS = {"trust","saves","sends","leads","sales"}
FIELDS = ("camera_presenter","target_audience","excluded_audience","post_goal","production_capacity")
VIDEOS = {"reel","video","live"}
QUESTIONS = {
    "fa": {
        "camera_presenter":"برای این ضبط چه کسی می‌تواند و می‌خواهد جلوی دوربین باشد؟ اگر هیچ‌کس نیست، بگو «بدون چهره».",
        "target_audience":"مخاطب دقیق این پست چه کسانی هستند؟",
        "excluded_audience":"این پست برای چه کسانی نیست؟",
        "post_goal":"هدف اصلی این پست چیست: اعتماد، ذخیره، ارسال، سرنخ یا فروش؟",
        "production_capacity":"برای ساخت این پست چه زمان و امکانات واقعی در دسترس است؟",
    },
    "en": {
        "camera_presenter":"Who is willing and available to appear on camera for this shoot? Say none for faceless.",
        "target_audience":"Who exactly is this post for?",
        "excluded_audience":"Who is this post NOT for?",
        "post_goal":"What is this post's ONE goal: trust, saves, sends, leads, or sales?",
        "production_capacity":"What time and production resources are available for this post?",
    },
}

def valid(key, value):
    if not isinstance(value,str) or not value.strip() or len(value)>1000:
        return False
    return value in GOALS if key=="post_goal" else True

def validate_defaults(brand):
    defaults=brand.get("post_defaults",{})
    if not isinstance(defaults,dict):
        raise ValueError("post_defaults must be object")
    for k,v in defaults.items():
        if k not in FIELDS or not valid(k,v):
            raise ValueError("Invalid post_defaults."+str(k))
    return defaults

def intake(brand,post=None,answers=None):
    if validator.validate_brand(brand):
        raise ValueError("Invalid brand profile: "+"; ".join(validator.validate_brand(brand)))
    defaults=validate_defaults(brand)
    post={} if post is None else post
    answers={} if answers is None else answers
    if not isinstance(post,dict) or not isinstance(answers,dict):
        raise ValueError("post and answers must be JSON objects")
    if set(post)-set(FIELDS)-{"format","post_id"}:
        raise ValueError("Unsupported post fields")
    if set(answers)-set(FIELDS):
        raise ValueError("Unsupported answer fields")
    fmt=post.get("format","reel")
    if fmt not in {"reel","video","live","caption","story","image","carousel"}:
        raise ValueError("Unsupported format")
    locale=brand["primary_locale"]
    keys=list(FIELDS[1:])
    if fmt in VIDEOS and brand.get("camera_policy")!="no":
        keys.insert(0,"camera_presenter")
    resolved={}
    missing=[]
    for k in keys:
        # The general audience can be reused if genuinely specified, but
        # placeholder template text is not an audience definition.
        fallback=defaults.get(k)
        if k=="target_audience" and fallback is None:
            broad=brand.get("target_audience")
            if isinstance(broad,str) and broad.strip() and not broad.lower().startswith("describe the actual audience"):
                fallback=broad
        if k=="excluded_audience" and fallback is None:
            fallback=brand.get("excluded_audience")
        if k=="production_capacity" and fallback is None:
            fallback=brand.get("production_capacity")
        v=answers.get(k,post.get(k,fallback))
        if k=="camera_presenter" and isinstance(v,str) and v.strip().lower() in ("none","بدون چهره","هیچ‌کس"):
            resolved[k]="none"
        elif valid(k,v):
            resolved[k]=v.strip()
        else:
            missing.append(k)
    if fmt in VIDEOS and brand.get("camera_policy")=="no":
        resolved["camera_presenter"]="none"
    return {
        "status":"READY" if not missing else "NEEDS_INPUT",
        "locale":locale,"format":fmt,"resolved":resolved,
        "missing_fields":missing,
        "questions":[{"field":k,"question":QUESTIONS[locale][k]} for k in missing],
        "write_performed":False,
        "note":"Single-post answers are not permanent brand defaults unless explicitly selected for --save",
    }

def save_durable(brand_path,answers,durable_keys):
    """Only explicit, whitelisted keys are persisted to the supplied brand file."""
    path=Path(brand_path)
    if not isinstance(answers,dict) or not isinstance(durable_keys,list):
        raise ValueError("answers must be object and durable_keys must be list")
    if not durable_keys or len(durable_keys)!=len(set(durable_keys)):
        raise ValueError("durable_keys must be nonempty, unique list")
    if set(durable_keys)-set(FIELDS):
        raise ValueError("Unsupported durable key")
    if any(k not in answers or not valid(k,answers[k]) for k in durable_keys):
        raise ValueError("Each durable key needs a valid explicit answer")
    original=path.read_text(encoding="utf-8")
    matches=list(validator.FENCE.finditer(original))
    if len(matches)!=1:
        raise ValueError("Exactly one JSON fence required for safe save")
    brand=validator.read_md(path)
    if validator.validate_brand(brand):
        raise ValueError("Cannot modify invalid brand profile")
    defaults=dict(validate_defaults(brand))
    defaults.update({k:answers[k].strip() for k in durable_keys})
    if brand.get("camera_policy")=="no" and "camera_presenter" in durable_keys and defaults["camera_presenter"].lower() not in ("none","بدون چهره","هیچ‌کس"):
        raise ValueError("Cannot save a presenter for a no-camera brand")
    brand["post_defaults"]=defaults
    if validator.validate_brand(brand):
        raise ValueError("Updated brand profile invalid")
    opening=chr(96)*3
    match=matches[0]
    updated=(original[:match.start()]+opening+"json\n"+
             json.dumps(brand,indent=2,ensure_ascii=False)+
             "\n"+opening+original[match.end():])
    fd,temp=tempfile.mkstemp(prefix=".brand-md-",suffix=".tmp",dir=str(path.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            f.write(updated)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return {"write_performed":True,"persisted_fields":durable_keys,"brand_path":str(path)}

def main():
    p=argparse.ArgumentParser(description="Private post intake; read-only unless --save")
    p.add_argument("--brand",required=True,type=Path)
    p.add_argument("--post",type=Path)
    p.add_argument("--answers",type=Path)
    p.add_argument("--save",action="store_true")
    args=p.parse_args()
    try:
        brand=validator.read_md(args.brand)
        post=json.loads(args.post.read_text(encoding="utf-8")) if args.post else None
        payload=json.loads(args.answers.read_text(encoding="utf-8")) if args.answers else {}
        if not isinstance(payload,dict):
            raise ValueError("Answers payload must be object")
        answer_map=payload.get("answers",{})
        result=intake(brand,post,answer_map)
        if args.save:
            if not args.answers:
                raise ValueError("--save requires --answers")
            result["persistence"]=save_durable(args.brand,answer_map,payload.get("durable_keys",[]))
            result["write_performed"]=True
        print(json.dumps(result,indent=2,ensure_ascii=False))
        return 0
    except (OSError,ValueError,TypeError) as e:
        print(json.dumps({"status":"INVALID","error":str(e)},ensure_ascii=False))
        return 2

if __name__=="__main__":
    sys.exit(main())
