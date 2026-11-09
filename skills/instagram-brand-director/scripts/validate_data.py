#!/usr/bin/env python3
"""Validate private brand.md, baseline.md and posts.csv; no network, no writes."""
import argparse, csv, io, json, re, sys
from datetime import date, datetime
from math import isfinite
from pathlib import Path

FORMATS = {"reel","carousel","story","image"}
GOALS = {"discovery","community","conversion","education"}
CAPABILITIES = {"on_camera","filming_products","motion_graphics","static_design","voiceover"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
FENCE = re.compile(r"(?ms)^\x60{3}json[ \t]*\n(.*?)\n\x60{3}[ \t]*$", re.I)
BASE_COLUMNS = ("post_id","published_at","format","goal","reach","likes","shares","saves","follows","source")
EXTRA_COLUMNS = ("trial","sku","metrics_age_hours")

def iso_date(s):
    try:
        return type(s) is str and date.fromisoformat(s).isoformat() == s
    except ValueError:
        return False

def read_md(path):
    matches = FENCE.findall(Path(path).read_text(encoding="utf-8"))
    if len(matches)!=1:
        raise ValueError("Exactly one JSON code fence required in Markdown")
    value=json.loads(matches[0])
    if type(value) is not dict:
        raise ValueError("Markdown JSON must be an object")
    return value

def validate_brand(d):
    errors=[]
    for k in ("schema_version","brand_id","name","primary_locale","camera_policy",
              "production_capabilities","target_audience","primary_goal"):
        if k not in d: errors.append("missing "+k)
    if type(d.get("schema_version")) is not int or d.get("schema_version")!=1:
        errors.append("schema_version must be integer 1")
    if type(d.get("brand_id")) is not str or not SLUG.fullmatch(d["brand_id"]):
        errors.append("invalid brand_id")
    for k in ("name","target_audience"):
        if type(d.get(k)) is not str or not d[k].strip():
            errors.append("invalid "+k)
    locale=d.get("primary_locale")
    registry_path=Path(__file__).resolve().parents[1]/"locales"/"registry.json"
    try:
        registry=json.loads(registry_path.read_text(encoding="utf-8"))
        supported=registry["locales"]
    except (OSError,KeyError,ValueError,TypeError):
        supported={}
    if (type(locale) is not str or locale not in supported or
        supported[locale].get("status")!="supported" or
        not (registry_path.parent/supported[locale].get("file","missing")).is_file()):
        errors.append("unsupported locale; add a reviewed locale file, registry entry and tests")
    if d.get("camera_policy") not in ("yes","no","unknown"):
        errors.append("camera_policy must be yes/no/unknown")
    caps=d.get("production_capabilities")
    if type(caps) is not list or any(type(x) is not str or x not in CAPABILITIES for x in caps) or len(caps)!=len(set(caps)):
        errors.append("invalid production_capabilities")
    elif d.get("camera_policy")=="no" and "on_camera" in caps:
        errors.append("no-camera policy conflicts with on_camera")
    if d.get("primary_goal") not in GOALS:
        errors.append("invalid primary_goal")
    if d.get("catalog_last_verified") is not None and not iso_date(d["catalog_last_verified"]):
        errors.append("invalid catalog_last_verified")
    if d.get("catalog_source") is not None and type(d["catalog_source"]) is not str:
        errors.append("invalid catalog_source")
    post_defaults=d.get("post_defaults",{})
    allowed_post_fields={"camera_presenter","target_audience","excluded_audience",
                         "post_goal","production_capacity"}
    if type(post_defaults) is not dict:
        errors.append("post_defaults must be object")
    else:
        for k,v in post_defaults.items():
            if k not in allowed_post_fields or type(v) is not str or not v.strip() or len(v)>1000:
                errors.append("invalid post_defaults."+str(k))
            elif k=="post_goal" and v not in {"trust","saves","sends","leads","sales"}:
                errors.append("invalid post_defaults.post_goal")
            elif k=="camera_presenter" and d.get("camera_policy")=="no" and v.lower() not in ("none","بدون چهره","هیچ‌کس"):
                errors.append("faceless brand cannot declare an on-camera presenter")
    return errors

def validate_baseline(d):
    errors=[]
    for k in ("schema_version","brand_id","as_of","window_start","format","primary_goal",
              "n_comparable_posts","total_reach","comparable","source","shares_per_reach"):
        if k not in d: errors.append("missing "+k)
    if type(d.get("schema_version")) is not int or d.get("schema_version")!=1:
        errors.append("schema_version must be integer 1")
    if type(d.get("brand_id")) is not str or not SLUG.fullmatch(d["brand_id"]):
        errors.append("invalid brand_id")
    for k in ("as_of","window_start"):
        if not iso_date(d.get(k)): errors.append("invalid "+k)
    if iso_date(d.get("as_of")) and iso_date(d.get("window_start")) and d["window_start"]>d["as_of"]:
        errors.append("window_start is after as_of")
    if d.get("format") not in FORMATS: errors.append("invalid format")
    if d.get("primary_goal") not in GOALS: errors.append("invalid primary_goal")
    for k in ("n_comparable_posts","total_reach"):
        if type(d.get(k)) is not int or d[k]<0: errors.append("invalid "+k)
    if type(d.get("comparable")) is not bool: errors.append("explicit comparable boolean required")
    if type(d.get("source")) is not str or not d["source"].strip(): errors.append("source required")
    for k in ("shares_per_reach","likes_per_reach","saves_per_reach","follows_per_reach"):
        if k in d and (type(d[k]) not in (int,float) or not isfinite(d[k]) or d[k]<0):
            errors.append("invalid rate "+k)
    if d.get("n_comparable_posts")==0 and d.get("total_reach",0)>0:
        errors.append("zero baseline posts with positive reach")
    return errors

def validate_posts_csv(s):
    reader=csv.DictReader(io.StringIO(s))
    if not reader.fieldnames: return ["missing CSV header"],0
    columns=[x.strip() for x in reader.fieldnames]
    if len(columns)!=len(set(columns)) or set(BASE_COLUMNS)-set(columns) or set(columns)-set(BASE_COLUMNS)-set(EXTRA_COLUMNS):
        return ["missing, duplicate or unknown columns"],0
    errors=[]; seen=set(); count=0
    for rowno,row in enumerate(reader,2):
        count+=1
        pid=(row.get("post_id") or "").strip()
        if not pid or pid in seen: errors.append(f"line {rowno}: missing or duplicate post_id")
        seen.add(pid)
        raw=(row.get("published_at") or "").strip()
        try:
            dt=datetime.fromisoformat(raw.replace("Z","+00:00"))
            if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError()
        except ValueError:
            errors.append(f"line {rowno}: published_at needs ISO timestamp with timezone")
        if (row.get("format") or "").strip() not in FORMATS:
            errors.append(f"line {rowno}: invalid format")
        if (row.get("goal") or "").strip() not in GOALS:
            errors.append(f"line {rowno}: invalid goal")
        if not (row.get("source") or "").strip():
            errors.append(f"line {rowno}: missing data source")
        if "metrics_age_hours" in row and row["metrics_age_hours"] not in ("",None):
            if not re.fullmatch(r"[0-9]+",row["metrics_age_hours"]):
                errors.append(f"line {rowno}: invalid metrics_age_hours")
        vals={}
        for key in ("reach","likes","shares","saves","follows"):
            s=(row.get(key) or "").strip()
            if not re.fullmatch(r"[0-9]+",s):
                errors.append(f"line {rowno}: invalid or missing {key}")
            else: vals[key]=int(s)
        if vals.get("reach")==0 and any(vals.get(k,0)>0 for k in ("likes","shares","saves","follows")):
            errors.append(f"line {rowno}: zero reach conflicts with engagements")
        if "trial" in row and row["trial"] not in ("","true","false"):
            errors.append(f"line {rowno}: trial must be true/false/blank")
    if count==0: errors.append("no post rows")
    return errors,count

def validate_file(kind,path):
    p=Path(path)
    if kind=="posts":
        errors,count=validate_posts_csv(p.read_text(encoding="utf-8-sig"))
        return {"type":kind,"valid":not errors,"rows":count,"errors":errors}
    data=read_md(p)
    errors=validate_brand(data) if kind=="brand" else validate_baseline(data)
    return {"type":kind,"valid":not errors,"errors":errors}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("kind",choices=("brand","baseline","posts"))
    p.add_argument("file",type=Path)
    a=p.parse_args()
    try: result=validate_file(a.kind,a.file)
    except (OSError,ValueError,json.JSONDecodeError) as e:
        result={"type":a.kind,"valid":False,"errors":[str(e)]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["valid"] else 1

if __name__=="__main__": sys.exit(main())
