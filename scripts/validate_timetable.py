"""Fail-closed validation for the optional theoretical pilot; independent of metro schema 1."""
import datetime as dt,hashlib,json,pathlib,re
from build_timetable import metro_scope,next_visit
def check(root=pathlib.Path('distribution'),now=None):
    network=json.loads((root/'network.json').read_text());scope=metro_scope(network)
    now=now or dt.datetime.now(dt.timezone.utc);target=root/'timetable';m=json.loads((target/'manifest.json').read_text())
    assert m['schemaVersion'] in (1,2) and m['quality']=='timetable' and set(m['lines'])==scope,'Invalid pilot schema/coverage'
    assert m['source']=='https://eu.ftp.opendatasoft.com/stif/GTFS/IDFM-gtfs.zip' and re.fullmatch('[a-f0-9]{64}',m['sourceSha256']),'Unproven source'
    assert hashlib.sha256((root/'network.json').read_bytes()).hexdigest()==m['networkSha256'],'Incompatible reference'
    network=json.loads((root/'network.json').read_text());allowed={(s,p['route_id'],p['stop_ids'][-1]) for p in network['patterns'] for i,s in enumerate(p['stop_ids'][:-1]) if p.get('stop_rules',[{}]*len(p['stop_ids']))[i].get('pickup_type','0')!='1'}
    start=dt.datetime.fromisoformat(m['validFromUtc']);end=dt.datetime.fromisoformat(m['validUntilUtc']);generated=dt.datetime.fromisoformat(m['generatedAtUtc'])
    assert start<=now<end and 0<=(now-generated).total_seconds()<172800,'Expired or future timetable'
    assert 0<(end-start).total_seconds()<=49*3600,'Invalid time window'
    points={s['stop_id']:s for s in network.get('stops',[])}
    next_edges=set()
    for pattern in network['patterns']:
        ids=pattern['stop_ids'];rules=pattern.get('stop_rules',[{}]*len(ids))
        for i,stop in enumerate(ids[:-1]):
            hop=next_visit(ids,rules,list(range(len(ids))),i,points)
            if hop:next_edges.add((pattern['route_id'],stop,hop[0]))
    count=0;groups=0
    for line,meta in m['lines'].items():
        assert meta['file']==line.replace(':','-')+'.json','Unexpected file'
        raw=(target/meta['file']).read_bytes();assert len(raw)==meta['bytes'] and len(raw)<=8_000_000 and hashlib.sha256(raw).hexdigest()==meta['sha256'],'Invalid timetable blob'
        d=json.loads(raw);assert d['schemaVersion']==m['schemaVersion'] and d['lineId']==line and d['validFromUtc']==m['validFromUtc'] and d['validUntilUtc']==m['validUntilUtc'],'Invalid line contract'
        for key,rows in d['groups'].items():
            stop,route,destination=json.loads(key);assert stop and destination and route==line and rows and (stop,route,destination) in allowed,'Invalid group/reference'
            previous=0
            for row in rows:
                assert len(row)==(6 if m['schemaVersion']==2 else 4) and isinstance(row[0],int) and start.timestamp()<=row[0]<end.timestamp() and row[0]>=previous,'Invalid instant/order'
                dt.date.fromisoformat(row[1]);assert re.fullmatch('[a-f0-9]{16}',row[2]) and isinstance(row[3],int) and row[3]>=0,'Invalid event identity'
                if m['schemaVersion']==2:
                    assert (line,stop,row[4]) in next_edges and row[4] in points and isinstance(row[5],int) and row[5]>row[3],'Invalid next stop'
                    assert (points[stop].get('parent_station') or stop)!=(points[row[4]].get('parent_station') or row[4]),'Next stop must leave departure place'
                previous=row[0];count+=1
            groups+=1
        assert len(d['groups'])==meta['groups'],'Incomplete groups'
    assert count==m['qa']['departures'] and groups==m['qa']['groups'],'Counts mismatch'
    return {'departures':count,'groups':groups,'valid_until':m['validUntilUtc']}
if __name__=='__main__':print('TIMETABLE_VALID',json.dumps(check()))

