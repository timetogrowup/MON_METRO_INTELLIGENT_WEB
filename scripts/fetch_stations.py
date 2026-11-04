"""Acquire full official metro stop/line associations, retaining all source IDs."""
import datetime, hashlib, json, pathlib, urllib.parse
from fetch_rail_segments import get, BASE

def main():
    dataset='arrets-lignes'
    metadata=get(f'{BASE}/{dataset}')
    fields={f['name'] for f in metadata['fields']}
    required={'mode','stop_name','route_long_name','pointgeo'}
    if not required <= fields:
        raise ValueError(f'Source schema changed: {sorted(fields)}')
    query=urllib.parse.urlencode({'where':'mode="Metro"'})
    total=get(f'{BASE}/{dataset}/records?{query}&limit=0')['total_count']
    rows=get(f'{BASE}/{dataset}/exports/json?{query}')
    if not isinstance(rows,list): raise ValueError('Invalid stations export')
    if not total or len(rows)!=total or len(rows)<100:
        raise ValueError(f'Incomplete stations: {len(rows)}/{total}')
    for row in rows:
        p=row.get('pointgeo') or {}
        if str(row.get('mode')).lower()!='metro' or not row.get('stop_name') or not (1<p.get('lon',0)<4 and 48<p.get('lat',0)<50):
            raise ValueError('Invalid metro station association')
    # Keep the complete source model. Master station deduplication awaits ID audit and GTFS.
    payload=(json.dumps({'schema_version':1,'associations':rows},ensure_ascii=False,separators=(',',':'))+'\n').encode()
    out=pathlib.Path('referentiel');out.mkdir(exist_ok=True)
    manifest={'dataset':dataset,'source':f'https://data.iledefrance-mobilites.fr/explore/dataset/{dataset}/',
              'downloaded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'association_count':len(rows),'source_fields':sorted(fields),'sha256':hashlib.sha256(payload).hexdigest(),
              'license_metadata':metadata.get('metas',{}),'status':'source-associations-not-deduplicated-master'}
    (out/'station_associations.json').write_bytes(payload)
    (out/'stations_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'association_count':len(rows),'fields':sorted(fields)}))
if __name__=='__main__':main()

