"""Publish a bounded, explicitly theoretical metro pilot from the verified GTFS cache."""
import collections, datetime as dt, hashlib, json, pathlib, zipfile
from zoneinfo import ZoneInfo
from build_gtfs import records, service_day, URL
def metro_scope(network):
    lines={r['route_id'] for r in network['lines'] if r['route_type']=='1'}
    if not lines or len(lines)>32:raise ValueError('Invalid metro scope')
    return lines
UTC=dt.timezone.utc
TZ=ZoneInfo('Europe/Paris')
def active_services(calendars, exceptions, day):
    stamp=day.strftime('%Y%m%d');weekday=['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][day.weekday()]
    active={r['service_id'] for r in calendars if r['start_date']<=stamp<=r['end_date'] and r[weekday]=='1'}
    for row in exceptions:
        if row['date']==stamp:
            if row['exception_type']=='1':active.add(row['service_id'])
            elif row['exception_type']=='2':active.discard(row['service_id'])
    return active

def seconds(value):
    h,m,s=map(int,value.split(':'))
    if not (0<=h<168 and 0<=m<60 and 0<=s<60):raise ValueError('Unsupported GTFS time')
    return h*3600+m*60+s

def instant(day,value):
    # GTFS time is elapsed time from local noon minus twelve hours, including DST days.
    noon=dt.datetime.combine(day,dt.time(12),TZ).astimezone(UTC)
    return int((noon-dt.timedelta(hours=12)+dt.timedelta(seconds=seconds(value))).timestamp())

def next_visit(ids,rules,numbers,index,stops):
    current=stops.get(ids[index],{}).get('parent_station') or ids[index]
    for j in range(index+1,len(ids)):
        r=rules[j]
        if r.get('pickup_type','0')=='1' and r.get('drop_off_type','0')=='1':continue
        place=stops.get(ids[j],{}).get('parent_station') or ids[j]
        if place!=current:return ids[j],numbers[j]
    return None


def trip_direction(trip):
    value=trip.get('direction_id','')
    if value not in ('','0','1',None):raise ValueError('Invalid GTFS direction_id')
    return value if value in ('0','1') else None

def validate_directions(data,required=False):
    if not required and data.get('directionVersion')!=1:return
    assert data.get('directionVersion')==1 and isinstance(data.get('tripDirections'),dict),'Missing GTFS directions'
    refs={row[2] for rows in data['groups'].values() for row in rows}
    assert set(data['tripDirections'])==refs,'Incomplete GTFS direction bindings'
    assert all(value in ('0','1',None) for value in data['tripDirections'].values()),'Invalid GTFS direction value'

def build(z,network,day):
    scope=metro_scope(network)
    agencies={r['agency_id']:r['agency_timezone'] for r in records(z,'agency')}
    routes={r['route_id']:r for r in records(z,'routes') if r['route_id'] in scope}
    if set(routes)!=scope:raise ValueError('Missing reference metro lines')
    if any(agencies.get(r['agency_id'])!='Europe/Paris' for r in routes.values()):raise ValueError('Unsupported agency timezone')
    calendars=list(records(z,'calendar')) if 'calendar.txt' in z.namelist() else []
    exceptions=list(records(z,'calendar_dates')) if 'calendar_dates.txt' in z.namelist() else []
    days=[day+dt.timedelta(days=i) for i in range(-7,2)]
    active={str(d):active_services(calendars,exceptions,d) for d in days}
    needed=set().union(*active.values())
    trips={r['trip_id']:r for r in records(z,'trips') if r['route_id'] in scope and r['service_id'] in needed}
    frequencies={r['trip_id'] for r in records(z,'frequencies')} if 'frequencies.txt' in z.namelist() else set()
    rows=collections.defaultdict(list)
    for r in records(z,'stop_times'):
        if r['trip_id'] in trips and r['trip_id'] not in frequencies:
            rows[r['trip_id']].append((int(r['stop_sequence']),r['stop_id'],r.get('departure_time',''),r.get('pickup_type','0'),r.get('drop_off_type','0')))
    stops={r['stop_id']:r for r in network.get('stops',[])}
    allowed=set()
    for p in network['patterns']:
        if p['route_id'] not in scope:continue
        for i,s in enumerate(p['stop_ids'][:-1]):
            if p.get('stop_rules',[{}]*len(p['stop_ids']))[i].get('pickup_type','0')!='1':allowed.add((s,p['route_id'],p['stop_ids'][-1]))
    start=int(dt.datetime.combine(day,dt.time(),TZ).timestamp());end=int(dt.datetime.combine(day+dt.timedelta(days=2),dt.time(),TZ).timestamp())
    directions={line:{} for line in scope};groups={line:{} for line in scope};count=0;unmatched=0;trip_ids=sorted(rows)
    for tid in trip_ids:
        seq=sorted(rows[tid]);trip=trips[tid]
        if len(seq)<2 or len({x[0] for x in seq})!=len(seq):raise ValueError('Invalid timetable sequence')
        times=[seconds(x[2]) for x in seq if x[2]]
        if times!=sorted(times):raise ValueError('Non-monotonic timetable')
        nexts={r[0]:next_visit([x[1] for x in seq],[{'pickup_type':x[3],'drop_off_type':x[4]} for x in seq],[x[0] for x in seq],i,stops) for i,r in enumerate(seq[:-1])}
        destination=seq[-1][1];tripref=hashlib.sha256(tid.encode()).hexdigest()[:16]
        for d in days:
            if trip['service_id'] not in active[str(d)]:continue
            for number,stop,value,pickup,dropoff in seq[:-1]:
                if not value or pickup=='1' or not nexts[number]:continue
                time=instant(d,value)
                if not start<=time<end:continue
                key=(stop,trip['route_id'],destination)
                if key not in allowed or (stops and nexts[number][0] not in stops):unmatched+=1;continue
                directions[trip['route_id']][tripref]=trip_direction(trip)
                encoded=json.dumps(key,separators=(',',':'));groups[trip['route_id']].setdefault(encoded,[]).append([time,str(d),tripref,number,*nexts[number]]);count+=1
    result={}
    for line,values in groups.items():
        if not values:raise ValueError('Empty metro timetable')
        for values_list in values.values():values_list.sort()
        result[line]={'directionVersion':1,'tripDirections':directions[line],'schemaVersion':2,'lineId':line,'validFromUtc':dt.datetime.fromtimestamp(start,UTC).isoformat(),'validUntilUtc':dt.datetime.fromtimestamp(end,UTC).isoformat(),'groups':values}
    return result,{'departures':count,'groups':sum(len(g) for g in groups.values()),'excluded_frequency_trips':len(frequencies&trips.keys()),'unmatched_reference_events':unmatched}

def main():
    day=service_day();archive=pathlib.Path('.cache')/f'gtfs-{day}.zip'
    if not archive.is_file():raise ValueError('Run build_gtfs.py first; verified daily cache required')
    network_bytes=pathlib.Path('distribution/network.json').read_bytes();network=json.loads(network_bytes)
    if network['service_date']!=str(day):raise ValueError('Reference must match generation day')
    with zipfile.ZipFile(archive) as z:result,qa=build(z,network,day)
    target=pathlib.Path('distribution/timetable');target.mkdir(parents=True,exist_ok=True);files={}
    for line,payload in sorted(result.items()):
        name=line.replace(':','-')+'.json';encoded=(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n').encode()
        if len(encoded)>8_000_000:raise ValueError('Timetable exceeds per-line budget')
        (target/name).write_bytes(encoded);files[line]={'file':name,'bytes':len(encoded),'sha256':hashlib.sha256(encoded).hexdigest(),'groups':len(payload['groups'])}
    manifest={'directionVersion':1,'schemaVersion':2,'quality':'timetable','source':URL,'attribution':'Île-de-France Mobilités — GTFS — ODbL','license_url':'https://opendatacommons.org/licenses/odbl/1-0/','generatedAtUtc':dt.datetime.now(UTC).isoformat(),'referenceDate':str(day),'networkSha256':hashlib.sha256(network_bytes).hexdigest(),'sourceSha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'validFromUtc':next(iter(result.values()))['validFromUtc'],'validUntilUtc':next(iter(result.values()))['validUntilUtc'],'lines':files,'qa':qa,'limitations':['Theoretical schedules only; no disruptions or live estimates.','Metro lines in the current reference; only matching boarding services.','Frequency-based trips excluded; empty results do not prove end of service.']}
    (target/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('TIMETABLE_OK',json.dumps(qa))
if __name__=='__main__':main()

