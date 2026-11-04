#!/usr/bin/env python3
"""Filter the versioned IDFM rail network to Metro features, retaining provenance."""
import json, pathlib, hashlib, datetime, sys
ROOT=pathlib.Path("referentiel")
def truthy(v):
    if isinstance(v,bool):return v
    if isinstance(v,(int,float)):return v==1
    return str(v).strip().lower() in {"1","true","oui","yes","vrai"}
def main():
    raw=json.loads((ROOT/"rail_segments_raw.geojson").read_text(encoding="utf-8"))
    source=json.loads((ROOT/"rail_manifest.json").read_text(encoding="utf-8"))
    features=raw.get("features",[])
    if not features:raise ValueError("Empty raw collection")
    metro=[]
    counts={}
    for feature in features:
        props=feature.get("properties") or {}
        for key in ("metro","mode","reseau"):
            v=props.get(key)
            counts.setdefault(key,{})[str(v)]=counts.setdefault(key,{}).get(str(v),0)+1
        # IDFM schema exposes a dedicated metro flag. Filter exclusively on it;
        # do not guess from the line name or a general rail-network category.
        if truthy(props.get("metro")):
            if feature.get("geometry",{}).get("type") not in ("LineString","MultiLineString"):
                raise ValueError("Invalid metro geometry")
            metro.append(feature)
    if len(metro)<100 or len(metro)==len(features):
        raise ValueError(f"Suspicious metro filter: {len(metro)}/{len(features)}. Sample attribute distributions: {str(counts)[:1500]}")
    collection={"type":"FeatureCollection","features":metro}
    data=(json.dumps(collection,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
    report={"source_dataset":source["dataset"],"source_sha256":source["sha256"],"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source_features":len(features),"metro_features":len(metro),"filter":"metro == true/1/oui","sha256":hashlib.sha256(data).hexdigest(),"attribute_counts":counts,"status":"geographic-segments-only-not-topological-network"}
    ROOT.mkdir(exist_ok=True)
    (ROOT/"metro_segments.geojson").write_bytes(data)
    (ROOT/"metro_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"source_features":len(features),"metro_features":len(metro),"filter":"metro flag"},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(1)

