"""Regional transport consultation packages. Never changes metro schema."""
import re, collections, datetime as dt, gzip, hashlib, json, pathlib, urllib.request, zipfile
from zoneinfo import ZoneInfo
from build_gtfs import records, service_day, URL
from build_timetable import active_services, instant, seconds, next_visit, trip_direction

ROOT=pathlib.Path('distribution/mobility')
LINE_URL='https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/referentiel-des-lignes/exports/json'
RER={'C01742':'A','C01743':'B','C01727':'C','C01728':'D','C01729':'E'}
BUS={'C01072':'20','C01073':'21','C01076':'26','C01083':'38','C01122':'91'}
SCOPE={**{k:'rer' for k in RER},**{k:'bus' for k in BUS}}
TZ=ZoneInfo('Europe/Paris');UTC=dt.timezone.utc

def encoded(value):return (json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
# Official line modes remain authoritative; names and GTFS rail codes alone
# cannot distinguish RER, Transilien, TER and airport shuttles.
GTFS_TYPES={'rer':{'2'},'bus':{'3'},'tram':{'0'},'train':{'2'},
            'ter':{'2'},'shuttle':{'0','2'},'cable':{'6'},'funicular':{'7'}}
def regional_mode(row):
    mode=row['transportmode']
    if mode in {'bus','tram','cableway','funicular'}:
        return {'cableway':'cable'}.get(mode,mode)
    if mode=='rail':
        if row['id_line'] in RER:return 'rer'
        if row.get('transportsubmode')=='suburbanRailway' and row.get('networkname')=='Transilien':return 'train'
        if row.get('transportsubmode')=='regionalRail' and row.get('networkname')=='TER':return 'ter'
        if row.get('transportsubmode')=='railShuttle':return 'shuttle'
    return None

def colour(value):
    value=str(value or '').strip().removeprefix('#')
    return value.upper() if re.fullmatch('[a-fA-F0-9]{6}',value) else ''

def classify(rows,all_bus=False):
    by_id={r['id_line']:r for r in rows};result={}
    scope=SCOPE if not all_bus else {**{k:'rer' for k in RER},**{r['id_line']:regional_mode(r) for r in rows if r['status']=='active' and regional_mode(r) is not None}}
    for identifier,mode in scope.items():
        r=by_id[identifier]
        if r['status']!='active':raise ValueError('Inactive scope line')
        if mode=='rer' and (r['transportmode']!='rail' or r['transportsubmode']!='local' or r['networkname']!='RER' or r['name_line']!=RER[identifier]):raise ValueError('Unproven RER classification')
        if mode=='bus' and (r['transportmode']!='bus' or (not all_bus and r['name_line']!=BUS[identifier])):raise ValueError('Unproven bus classification')
        result['IDFM:'+identifier]={'route_id':'IDFM:'+identifier,'route_short_name':r['name_line'],'mode':mode,'operator':r['operatorname'],'route_color':colour(r.get('colourweb_hexa')),'route_text_color':colour(r.get('textcolourweb_hexa'))}
    return result

def build(z,source_lines,day,all_bus=False):
    lines=classify(source_lines,all_bus);routes={r['route_id']:r for r in records(z,'routes') if r['route_id'] in lines}
    if not all_bus and set(routes)!=set(lines):raise ValueError('Missing pilot line in GTFS')
    agencies={r['agency_id']:r['agency_timezone'] for r in records(z,'agency')}
    for key,r in routes.items():
        if r['route_type'] not in GTFS_TYPES[lines[key]['mode']] or agencies.get(r['agency_id'])!='Europe/Paris':raise ValueError('GTFS mode/timezone mismatch')
    days=[day+dt.timedelta(days=i) for i in range(-7,4)]
    calendars=list(records(z,'calendar')) if 'calendar.txt' in z.namelist() else []
    exceptions=list(records(z,'calendar_dates')) if 'calendar_dates.txt' in z.namelist() else []
    active={str(d):active_services(calendars,exceptions,d) for d in days};needed=set().union(*active.values())
    trips={r['trip_id']:r for r in records(z,'trips') if r['route_id'] in lines and r['service_id'] in needed}
    freq={r['trip_id'] for r in records(z,'frequencies')} if 'frequencies.txt' in z.namelist() else set()
    rows=collections.defaultdict(list)
    for r in records(z,'stop_times'):
        if r['trip_id'] in trips and r['trip_id'] not in freq:rows[r['trip_id']].append({k:r.get(k,'') for k in ('stop_id','stop_sequence','departure_time','pickup_type','drop_off_type')})
    start=int(dt.datetime.combine(day,dt.time(),TZ).timestamp());end=int(dt.datetime.combine(day+dt.timedelta(days=4),dt.time(),TZ).timestamp())
    bounds={'validFromUtc':dt.datetime.fromtimestamp(start,UTC).isoformat(),'validUntilUtc':dt.datetime.fromtimestamp(end,UTC).isoformat()}
    stops={r['stop_id']:r for r in records(z,'stops')}
    directions={k:{} for k in lines};groups={k:{} for k in lines};patterns={};used=set();omitted_conditional=0
    for tid,raw in rows.items():
        seq=sorted(raw,key=lambda r:int(r['stop_sequence']));trip=trips[tid];line=trip['route_id'];destination=seq[-1]['stop_id']
        if len(seq)<2 or len({r['stop_sequence'] for r in seq})!=len(seq):raise ValueError('Invalid sequence')
        times=[seconds(r['departure_time']) for r in seq if r['departure_time']]
        if times!=sorted(times):raise ValueError('Non-monotonic trip')
        nexts={int(r['stop_sequence']):next_visit([x['stop_id'] for x in seq],seq,[int(x['stop_sequence']) for x in seq],i,stops) for i,r in enumerate(seq[:-1])}
        valid_rows=[];tripref=digest(tid.encode())[:16]
        for d in days:
            if trip['service_id'] not in active[str(d)]:continue
            for r in seq[:-1]:
                if r.get('pickup_type','0') not in ('','0'):
                    omitted_conditional+=1;continue
                if not r['departure_time'] or not nexts[int(r['stop_sequence'])]:continue
                stamp=instant(d,r['departure_time'])
                if start<=stamp<end:valid_rows.append((r,stamp,str(d)))
        if not valid_rows:continue
        pkey=json.dumps([line,[(r['stop_id'],r.get('pickup_type','0'),r.get('drop_off_type','0')) for r in seq]],separators=(',',':'))
        patterns.setdefault(pkey,{'id':digest(pkey.encode())[:24],'route_id':line,'stop_ids':[r['stop_id'] for r in seq],'stop_rules':[{'pickup_type':'0' if r.get('pickup_type','0') in ('','0') else '1','drop_off_type':r.get('drop_off_type','0')} for r in seq]})
        used.update(r['stop_id'] for r in seq)
        for r,stamp,date in valid_rows:
            key=json.dumps([r['stop_id'],line,destination],separators=(',',':'))
            directions[line][tripref]=trip_direction(trip)
            groups[line].setdefault(key,[]).append([stamp,date,tripref,int(r['stop_sequence']),*nexts[int(r['stop_sequence'])]])
    stops={r['stop_id']:r for r in records(z,'stops')};parents={stops[s].get('parent_station') or s for s in used}
    selected={k:stops[k] for k in used|parents}
    stations=[];points_by_parent=collections.defaultdict(list)
    for k in used:points_by_parent[stops[k].get('parent_station') or k].append(k)
    for parent in sorted(parents):
        s=stops[parent];lat=float(s['stop_lat']);lon=float(s['stop_lon'])
        if not (47<lat<51 and 0<lon<6):raise ValueError('Invalid pilot coordinates')
        stations.append({'id':parent,'name':s['stop_name'],'lat':lat,'lon':lon,'stop_point_ids':sorted(points_by_parent[parent])})
    index={'schemaVersion':2,'kind':'consultation-only','service_date':str(day),**bounds,'lines':list(lines.values()),'stops':list(selected.values()),'stations':stations,'patterns':sorted(patterns.values(),key=lambda p:p['id'])}
    packages={};counts={}
    for line,values in sorted(groups.items()):
        if not values and not all_bus:raise ValueError('No dated departures for pilot line '+line)
        for seq in values.values():seq.sort()
        packages[line]={'directionVersion':1,'tripDirections':directions[line],'schemaVersion':2,'lineId':line,**bounds,'groups':values}
        counts[line]={'groups':len(values),'departures':sum(map(len,values.values()))}
    return index,packages,{'lines':counts,'excluded_frequency_trips':len(freq&trips.keys()),'excluded_conditional_boarding_rows':omitted_conditional}

def main():
    day=service_day();archive=pathlib.Path('.cache')/f'gtfs-{day}.zip'
    if not archive.is_file():raise ValueError('Verified daily GTFS cache required')
    raw=urllib.request.urlopen(urllib.request.Request(LINE_URL,headers={'User-Agent':'wenare/1.0'}),timeout=45).read(8_000_001)
    if len(raw)>8_000_000:raise ValueError('Line reference size budget exceeded')
    if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
    if len(raw)>8_000_000:raise ValueError('Decompressed line reference budget exceeded')
    source_lines=json.loads(raw)
    with zipfile.ZipFile(archive) as z:index,packages,qa=build(z,source_lines,day)
    ROOT.mkdir(parents=True,exist_ok=True);index_raw=encoded(index);(ROOT/'index.json').write_bytes(index_raw);files={}
    if len(index_raw)>4_000_000:raise ValueError('Index size budget exceeded')
    for line,data in packages.items():
        name=line.replace(':','-')+'.json';payload=encoded(data)
        if len(payload)>8_000_000:raise ValueError('Line package budget exceeded '+line)
        (ROOT/name).write_bytes(payload);files[line]={'file':name,'bytes':len(payload),'sha256':digest(payload),'groups':len(data['groups'])}
    manifest={'directionVersion':1,'schemaVersion':2,'quality':'timetable','source':URL,'attribution':'Île-de-France Mobilités — GTFS (Licence Mobilité) et référentiel des lignes (ODbL)','sourcePage':'https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/','license_url':'https://cloud.fabmob.io/s/eYWWJBdM3fQiFNm','lineSource':LINE_URL,'lineSourceSha256':digest(raw),'sourceSha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'networkSha256':digest(index_raw),'index':{'file':'index.json','bytes':len(index_raw),'sha256':digest(index_raw)},'generatedAtUtc':dt.datetime.now(UTC).isoformat(),'referenceDate':str(day),'validFromUtc':index['validFromUtc'],'validUntilUtc':index['validUntilUtc'],'lines':files,'scope':SCOPE,'qa':qa,'limitations':['Consultation only. RER A-E and bus 20/21/26/38/91 pilot, not all buses.','Theoretical schedules; no disruption, live location or boarding inference.','Conditional boarding and frequency-based services omitted.']}
    (ROOT/'manifest.json').write_bytes(encoded(manifest));print('MOBILITY_BUILT',json.dumps({'indexBytes':len(index_raw),'packages':files,'qa':qa}))

if __name__=='__main__':main()


