"""Build date-scoped metro patterns from official GTFS, never infer rail proximity as ridership."""
import collections, csv, datetime, hashlib, io, json, pathlib, tempfile, urllib.request, zipfile, time, shutil
URL='https://eu.ftp.opendatasoft.com/stif/GTFS/IDFM-gtfs.zip'
from zoneinfo import ZoneInfo
OUT=pathlib.Path('referentiel/gtfs')
def service_day():
    return datetime.datetime.now(ZoneInfo('Europe/Paris')).date()

def records(z, name):
    with z.open(name+'.txt') as f:
        yield from csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig',newline=''))

def build(z, day):
    stamp=day.strftime('%Y%m%d'); weekday=day.strftime('%A').lower()
    services=set()
    if 'calendar.txt' in z.namelist():
        services={r['service_id'] for r in records(z,'calendar') if r['start_date']<=stamp<=r['end_date'] and r[weekday]=='1'}
    if 'calendar_dates.txt' in z.namelist():
        for r in records(z,'calendar_dates'):
            if r['date']==stamp:
                if r['exception_type']=='1':services.add(r['service_id'])
                elif r['exception_type']=='2':services.discard(r['service_id'])
    routes={r['route_id']:r for r in records(z,'routes') if r['route_type']=='1'}
    trips={r['trip_id']:r for r in records(z,'trips') if r['route_id'] in routes and r['service_id'] in services}
    if not trips: raise ValueError('No active metro trips for reference date')
    sequences=collections.defaultdict(list)
    for r in records(z,'stop_times'):
        if r['trip_id'] in trips:
            sequences[r['trip_id']].append((int(r['stop_sequence']),r['stop_id'],r.get('pickup_type','0'),r.get('drop_off_type','0')))
    patterns={};used=set();edges=set()
    for tid,t in trips.items():
        seq=sorted(sequences.get(tid,[]));numbers=[x[0] for x in seq]
        if len(seq)<2 or len(numbers)!=len(set(numbers)):raise ValueError(f'Invalid stop sequence {tid}')
        stop_ids=tuple(x[1] for x in seq)
        key=(t['route_id'],t.get('direction_id',''),tuple((x[1],x[2],x[3]) for x in seq))
        if key not in patterns:
            pid=hashlib.sha256(json.dumps(key).encode()).hexdigest()[:24]
            patterns[key]={'id':pid,'route_id':t['route_id'],'direction_id':t.get('direction_id'),
                'stop_ids':stop_ids,'stop_rules':[{'stop_id':x[1],'pickup_type':x[2],'drop_off_type':x[3]} for x in seq],
                'example_trip_id':tid,'headsign':t.get('trip_headsign'),'shape_id':t.get('shape_id'),'trip_count':0}
        patterns[key]['trip_count']+=1
        used.update(stop_ids)
        edges.update((t['route_id'],a,b) for a,b in zip(stop_ids,stop_ids[1:]))
    all_stops={r['stop_id']:r for r in records(z,'stops')}
    if used-all_stops.keys():raise ValueError('Unknown stop references')
    parents={all_stops[s].get('parent_station') for s in used}-{None,''}
    if parents-all_stops.keys():raise ValueError('Unknown parent stations')
    stops={s:all_stops[s] for s in used|parents}
    for s in stops.values():
        if not (1<float(s['stop_lon'])<4 and 48<float(s['stop_lat'])<50):raise ValueError('Invalid GTFS coordinates')
    transfers=[]
    if 'transfers.txt' in z.namelist():
        transfers=[r for r in records(z,'transfers') if r['from_stop_id'] in stops and r['to_stop_id'] in stops]
    shape_ids={p['shape_id'] for p in patterns.values()}-{None,''}
    shapes=collections.defaultdict(list)
    if shape_ids and 'shapes.txt' in z.namelist():
        for r in records(z,'shapes'):
            if r['shape_id'] in shape_ids:
                shapes[r['shape_id']].append((int(r['shape_pt_sequence']),float(r['shape_pt_lon']),float(r['shape_pt_lat'])))
    shape_features=[]
    for sid,points in sorted(shapes.items()):
        points.sort()
        if len(points)<2: raise ValueError('Invalid GTFS shape')
        shape_features.append({'type':'Feature','properties':{'shape_id':sid},
            'geometry':{'type':'LineString','coordinates':[[lon,lat] for _,lon,lat in points]}})
    route_ids={t['route_id'] for t in trips.values()}
    return {'stops':[stops[k] for k in sorted(stops)],'lines':[routes[k] for k in sorted(route_ids)],
            'patterns':sorted(patterns.values(),key=lambda x:x['id']),
            'edges':[{'route_id':r,'from_stop_id':a,'to_stop_id':b} for r,a,b in sorted(edges)],
            'transfers':transfers,'shapes':shape_features,'inactive_lines':[routes[k] for k in sorted(set(routes)-route_ids)]}

def main():
    with tempfile.TemporaryDirectory() as tmp:
        archive=pathlib.Path(tmp)/'gtfs.zip'
        cache=pathlib.Path('.cache')/('gtfs-'+str(service_day())+'.zip')
        if cache.exists() and zipfile.is_zipfile(cache):
            shutil.copyfile(cache,archive)
            print('Using verified daily GTFS archive cache')
        else:
            for attempt in range(3):
                try:
                    size=0
                    request=urllib.request.Request(URL,headers={'User-Agent':'MonMetroIntelligent/2.0','Accept':'application/zip'})
                    with urllib.request.urlopen(request,timeout=90) as response, archive.open('wb') as target:
                        while block:=response.read(1024*1024):
                            size+=len(block)
                            if size>300*1024*1024:raise ValueError('GTFS exceeds download budget 300 MiB')
                            target.write(block)
                    if not zipfile.is_zipfile(archive):raise ValueError('GTFS endpoint returned a non-ZIP response')
                    cache.parent.mkdir(exist_ok=True);shutil.copyfile(archive,cache)
                    break
                except Exception as exc:
                    print(f'GTFS acquisition attempt {attempt+1} failed: {type(exc).__name__}')
                    if attempt==2:raise
                    time.sleep(2*(attempt+1))
        digest=hashlib.sha256();size=0
        with archive.open('rb') as content:
            while block:=content.read(1024*1024):digest.update(block);size+=len(block)
        if size>300*1024*1024:raise ValueError('Cached GTFS exceeds size budget')
        day=service_day()
        with zipfile.ZipFile(archive) as z:
            if sum(i.file_size for i in z.infolist())>8*1024**3:raise ValueError('GTFS decompressed size exceeds budget')
            result=build(z,day)
        OUT.mkdir(parents=True,exist_ok=True);files={}
        for name,data in result.items():
            encoded=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
            (OUT/(name+'.json')).write_bytes(encoded)
            files[name]={'count':len(data),'sha256':hashlib.sha256(encoded).hexdigest()}
        manifest={'source':URL,'source_page':'https://transport.data.gouv.fr/resources/80921',
            'downloaded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'service_date':str(day),
            'source_sha256':digest.hexdigest(),'download_bytes':size,'files':files,
            'status':'ordered-service-graph-not-matched-to-rail-geometries',
            'limitations':['Only services active on reference date. Refresh daily before use.',
                'GTFS directions are source codes, not user-facing terminus labels.',
                'No spatial matching or phone/field validation performed.']}
        (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__':main()

