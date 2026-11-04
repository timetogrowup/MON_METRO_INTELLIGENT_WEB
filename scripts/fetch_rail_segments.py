#!/usr/bin/env python3
"""Fetch and validate public IDFM rail segments; never replace valid data with failed downloads."""
import json, urllib.request, urllib.parse, pathlib, datetime, hashlib, sys, gzip
BASE="https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets"
DATASET="traces-du-reseau-ferre-idf"
OUT=pathlib.Path("referentiel")
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"MonMetroIntelligent/1.3 (GitHub Actions)","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as r:
        raw=r.read()
        encoding=r.headers.get("Content-Encoding","").lower()
        if encoding=="gzip" or raw[:2]==bytes([0x1f,0x8b]):
            raw=gzip.decompress(raw)
        return json.loads(raw.decode("utf-8-sig"))
def main():
    meta=get(f"{BASE}/{DATASET}")
    print("Dataset metadata:",json.dumps({"dataset_id":meta.get("dataset_id"),"fields":[x.get("name") for x in meta.get("fields",[])]},ensure_ascii=False))
    fields={x.get("name") for x in meta.get("fields",[])}
    geom=next((x for x in ("geo_shape","geoshape","geometry") if x in fields),None)
    if not geom:raise ValueError("No recognized geometry field; inspect dataset schema")
    # A single export avoids unstable page boundaries in the live source.
    total=get(f"{BASE}/{DATASET}/records?limit=0")["total_count"]
    records=get(f"{BASE}/{DATASET}/exports/json")
    if not isinstance(records,list) or not records or len(records)!=total:
        raise ValueError(f"Incomplete snapshot {len(records) if isinstance(records,list) else 'invalid'}/{total}")
    features=[]
    sample_shapes=[]
    for row in records:
        shape=row.get(geom)
        if isinstance(shape,str):
            try:shape=json.loads(shape)
            except json.JSONDecodeError:continue
        if not isinstance(shape,dict):continue
        if len(sample_shapes)<3:sample_shapes.append({"type":shape.get("type"),"keys":list(shape.keys())})
        # Opendatasoft's geo_shape can be a GeoJSON Feature wrapper.
        if shape.get("type")=="Feature":
            shape=shape.get("geometry")
        if not isinstance(shape,dict):continue
        if shape.get("type") not in ("LineString","MultiLineString"):continue
        coordinates=shape.get("coordinates")
        if not coordinates:continue
        props={k:v for k,v in row.items() if k!=geom}
        features.append({"type":"Feature","geometry":shape,"properties":props})
    if not features:raise ValueError("No usable line geometries; sample shape metadata: "+repr(sample_shapes))
    # Keep source mode attributes: rail dataset may also include RER/tram.
    # Do not claim metro-only coverage until mode mapping has been audited.
    geo={"type":"FeatureCollection","features":features}
    encoded=(json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n").encode()
    manifest={"source":f"https://data.iledefrance-mobilites.fr/explore/dataset/{DATASET}/","dataset":DATASET,"downloaded_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source_records":len(records),"valid_line_geometries":len(features),"geometry_field":geom,"scope":"rail-all-modes-unfiltered","acquisition":"single-export-json","license_metadata":meta.get("metas",{}),"sha256":hashlib.sha256(encoded).hexdigest()}
    OUT.mkdir(exist_ok=True)
    (OUT/"rail_segments_raw.geojson").write_bytes(encoded)
    (OUT/"rail_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("Validated:",json.dumps(manifest,ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as e:print(f"FAILED: {type(e).__name__}: {e}",file=sys.stderr);sys.exit(1)

