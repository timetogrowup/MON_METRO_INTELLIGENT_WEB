"""All supported officially active IDFM transport modes; compact catalogue, lazy per-line schedules."""
import datetime as dt, gzip, hashlib, json, pathlib, urllib.request, zipfile
from build_gtfs import records, service_day, URL
from build_mobility import build, classify, encoded, digest, LINE_URL, UTC
ROOT=pathlib.Path('distribution/mobility')
INDEX_LIMIT=24_000_000

def compact(index,packages):
    services=[json.loads(key) for p in packages.values() for key in p['groups']]
    return {'schemaVersion':3,'kind':'consultation-only','service_date':index['service_date'],
            'validFromUtc':index['validFromUtc'],'validUntilUtc':index['validUntilUtc'],
            'lines':index['lines'],'packed':{
                'stops':[[s['stop_id'],s['stop_name'],s.get('parent_station') or '',s.get('platform_code') or ''] for s in index['stops']],
                'stations':[[s['id'],s['name'],s['lat'],s['lon'],s['stop_point_ids']] for s in index['stations']],
                'services':services}}

def main():
    day=service_day();archive=pathlib.Path('.cache')/f'gtfs-{day}.zip'
    if not archive.is_file():raise ValueError('Verified daily GTFS cache required')
    raw=urllib.request.urlopen(urllib.request.Request(LINE_URL,headers={'User-Agent':'wenare/1.0'}),timeout=60).read(8_000_001)
    if len(raw)>8_000_000:raise ValueError('Line reference budget exceeded')
    if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
    if len(raw)>8_000_000:raise ValueError('Line reference budget exceeded')
    source_lines=json.loads(raw);lines=classify(source_lines,all_bus=True)
    with zipfile.ZipFile(archive) as z:
        gtfs_ids={r['route_id'] for r in records(z,'routes')}
        index,packages,qa=build(z,source_lines,day,all_bus=True)
    statuses={line:('dated_departures' if p['groups'] else 'no_dated_departures' if line in gtfs_ids else 'absent_from_gtfs') for line,p in packages.items()}
    index=compact(index,packages);index['coverage']=statuses
    ROOT.mkdir(parents=True,exist_ok=True);(ROOT/'lines-source.json').write_bytes(raw);payload=encoded(index)
    if len(payload)>INDEX_LIMIT:raise ValueError('Compact regional index exceeds mobile budget')
    (ROOT/'index.json').write_bytes(payload);files={}
    for line,p in packages.items():
        name=line.replace(':','-')+'.json';b=encoded(p)
        if len(b)>8_000_000:raise ValueError('Line package exceeds budget '+line)
        (ROOT/name).write_bytes(b);files[line]={'file':name,'bytes':len(b),'sha256':digest(b),'groups':len(p['groups'])}
    qa['coverage']={state:sum(s==state for s in statuses.values()) for state in set(statuses.values())}
    qa['modeLines']={mode:sum(v['mode']==mode for v in lines.values()) for mode in sorted({v['mode'] for v in lines.values()})}
    qa['busLines']=qa['modeLines'].get('bus',0)
    m={'directionVersion':1,'schemaVersion':2,'catalogueVersion':3,'quality':'timetable','source':URL,
       'attribution':'Île-de-France Mobilités — GTFS (Licence Mobilité) et référentiel des lignes (ODbL)',
       'sourcePage':'https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/',
       'license_url':'https://cloud.fabmob.io/s/eYWWJBdM3fQiFNm',
       'lineSource':LINE_URL,'lineSourceSha256':digest(raw),
       'sourceSha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),
       'networkSha256':digest(payload),'index':{'file':'index.json','bytes':len(payload),'sha256':digest(payload)},
       'generatedAtUtc':dt.datetime.now(UTC).isoformat(),'referenceDate':str(day),
       'validFromUtc':index['validFromUtc'],'validUntilUtc':index['validUntilUtc'],
       'lines':files,'scope':{k.removeprefix('IDFM:'):v['mode'] for k,v in lines.items()},'qa':qa,
       'limitations':['Active official bus, RER, tram, Transilien, TER, airport shuttle, cableway and funicular lines catalogued; only dated GTFS departures can be displayed.',
                       'No live information or disruptions. Conditional boarding and frequency services omitted.']}
    (ROOT/'manifest.json').write_bytes(encoded(m))
    print('BUS_IDF_BUILT',json.dumps({'busLines':qa['busLines'],'coverage':qa['coverage'],'indexBytes':len(payload),'places':len(index['packed']['stations']),'departures':sum(v['departures'] for v in qa['lines'].values())}))
if __name__=='__main__':main()
