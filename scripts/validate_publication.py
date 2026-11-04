"""Validate the exact public bundle before an atomic two-file publication."""
import argparse, datetime, hashlib, json, math, pathlib, re
from zoneinfo import ZoneInfo
MAX_BYTES=10*1024*1024

def paris_day(now=None):
    return (now or datetime.datetime.now(datetime.timezone.utc)).astimezone(ZoneInfo('Europe/Paris')).date()

def validate(raw, manifest, expected_date):
    if manifest.get('schema_version')!=1 or manifest.get('file')!='network.json':raise ValueError('Unsupported publication schema/path')
    if not 0<len(raw)<=MAX_BYTES or manifest.get('bytes')!=len(raw):raise ValueError('Invalid publication size')
    digest=hashlib.sha256(raw).hexdigest()
    if manifest.get('sha256')!=digest or manifest.get('version')!=digest[:24]:raise ValueError('Publication hash/version mismatch')
    if manifest.get('service_date')!=str(expected_date):raise ValueError('Public service date must match today in Europe/Paris')
    if not re.fullmatch('[a-f0-9]{64}',manifest.get('source_gtfs_sha256','')):raise ValueError('Missing GTFS provenance hash')
    data=json.loads(raw)
    if data.get('schema_version')!=1 or data.get('service_date')!=manifest['service_date']:raise ValueError('Payload schema/date mismatch')
    groups={}
    for name,key in [('stations','id'),('lines','route_id'),('stops','stop_id'),('patterns','id')]:
        items=data.get(name)
        if not isinstance(items,list) or not items or len(items)!=manifest.get('counts',{}).get(name):raise ValueError('Invalid collection: '+name)
        ids=[v.get(key) for v in items]
        if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):raise ValueError('Missing/duplicate identifiers: '+name)
        groups[name]=dict(zip(ids,items))
    segments=data.get('segments')
    if not isinstance(segments,list) or not segments or len(segments)!=manifest['counts'].get('segments'):raise ValueError('Invalid segments count')
    ids=set(); covered=set()
    for stop in groups['stops'].values():
        parent=stop.get('parent_station')
        if parent and parent not in groups['stops']:raise ValueError('Unknown parent station')
        lon,lat=float(stop['stop_lon']),float(stop['stop_lat'])
        if not(1<lon<4 and 48<lat<50):raise ValueError('Stop outside IDF')
    for pattern in groups['patterns'].values():
        points=pattern.get('stop_ids',[])
        if pattern.get('route_id') not in groups['lines'] or len(points)<2 or any(s not in groups['stops'] for s in points):raise ValueError('Invalid pattern references')
        if any(s not in groups['stations'] for s in pattern.get('station_ids',[])):raise ValueError('Invalid master station references')
    for station in groups['stations'].values():
        if any(s not in groups['stops'] for s in station.get('stop_point_ids',[])):raise ValueError('Invalid master stop point')
        if any(r not in groups['lines'] for r in station.get('route_ids',[])):raise ValueError('Invalid master route')
    for segment in segments:
        p=segment.get('properties',{});sid=p.get('id');pattern=groups['patterns'].get(p.get('pattern_id'));sequence=p.get('sequence')
        if not isinstance(sid,str) or sid in ids:raise ValueError('Missing/duplicate segment id')
        ids.add(sid)
        if pattern is None or type(sequence) is not int or not 0<=sequence<len(pattern['stop_ids'])-1:raise ValueError('Invalid segment pattern/sequence')
        if p.get('route_id')!=pattern['route_id'] or [p.get('from_stop_id'),p.get('to_stop_id')]!=pattern['stop_ids'][sequence:sequence+2]:raise ValueError('Segment endpoint mismatch')
        geometry=segment.get('geometry',{});coords=geometry.get('coordinates',[])
        if geometry.get('type')!='LineString' or len(coords)<2:raise ValueError('Invalid directed geometry')
        for point in coords:
            if len(point)<2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in point[:2]) or not (1<point[0]<4 and 48<point[1]<50):raise ValueError('Invalid coordinate')
        if len({tuple(point[:2]) for point in coords})<2:raise ValueError('Degenerate geometry')
        covered.add((pattern['id'],sequence))
    expected={(p['id'],i) for p in groups['patterns'].values() for i in range(len(p['stop_ids'])-1)}
    if covered!=expected or len(covered)!=len(segments):raise ValueError('Incomplete or duplicated directed edge coverage')
    return {'service_date':manifest['service_date'],'sha256':digest,'bytes':len(raw),'counts':manifest['counts'],'status':'validated-for-two-file-publication'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--directory',default='distribution');parser.add_argument('--service-date');args=parser.parse_args()
    root=pathlib.Path(args.directory);day=datetime.date.fromisoformat(args.service_date) if args.service_date else paris_day()
    report=validate((root/'network.json').read_bytes(),json.loads((root/'manifest.json').read_text()),day)
    print(json.dumps(report,ensure_ascii=False))

