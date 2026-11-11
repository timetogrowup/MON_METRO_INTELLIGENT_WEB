from build_timetable import validate_directions
"""Validate isolated consultation data, exact pilot scope and all event bindings."""
import datetime as dt, hashlib, json, pathlib, re
from build_mobility import SCOPE
from build_timetable import next_visit

def check(root=pathlib.Path('distribution/mobility'),now=None):
    now=now or dt.datetime.now(dt.timezone.utc);m=json.loads((root/'manifest.json').read_bytes());raw=(root/'index.json').read_bytes();d=json.loads(raw)
    if m.get('catalogueVersion')==3:
        from validate_bus_network import check as regional_check
        return regional_check(root,now)
    expected={'IDFM:'+k:v for k,v in SCOPE.items()}
    assert m['schemaVersion'] in (1,2) and m['quality']=='timetable' and m['scope']==SCOPE
    assert m['source']=='https://eu.ftp.opendatasoft.com/stif/GTFS/IDFM-gtfs.zip' and re.fullmatch('[a-f0-9]{64}',m['sourceSha256'])
    assert re.fullmatch('[a-f0-9]{64}',m['lineSourceSha256'])
    start=dt.datetime.fromisoformat(m['validFromUtc']);end=dt.datetime.fromisoformat(m['validUntilUtc']);generated=dt.datetime.fromisoformat(m['generatedAtUtc'])
    assert start<=now<end and 0<=(now-generated).total_seconds()<172800 and 0<(end-start).total_seconds()<=97*3600
    assert m['index']['file']=='index.json' and len(raw)==m['index']['bytes'] and len(raw)<=4_000_000
    assert hashlib.sha256(raw).hexdigest()==m['index']['sha256']==m['networkSha256']
    assert d['schemaVersion']==2 and d['kind']=='consultation-only' and d['validFromUtc']==m['validFromUtc'] and d['validUntilUtc']==m['validUntilUtc']
    assert {r['route_id']:r['mode'] for r in d['lines']}==expected and len(d['lines'])==len(expected) and set(m['lines'])==set(expected)
    stops={s['stop_id']:s for s in d['stops']};assert len(stops)==len(d['stops'])
    places=set();bound=set()
    for s in d['stations']:
        assert s['id'] not in places and s['id'] in stops and s['name'] and 47<s['lat']<51 and 0<s['lon']<6 and s['stop_point_ids'];places.add(s['id'])
        for p in s['stop_point_ids']:
            assert p in stops and p not in bound and (stops[p].get('parent_station') or p)==s['id'];bound.add(p)
    allowed=set();next_edges=set()
    for p in d['patterns']:
        assert p['route_id'] in expected and len(p['stop_ids'])>=2 and len(p['stop_ids'])==len(p['stop_rules']) and set(p['stop_ids'])<=bound
        for i,s in enumerate(p['stop_ids'][:-1]):
            hop=next_visit(p['stop_ids'],p['stop_rules'],list(range(len(p['stop_ids']))),i,stops)
            if hop:next_edges.add((p['route_id'],s,hop[0]))
            if p['stop_rules'][i]['pickup_type']=='0':allowed.add((s,p['route_id'],p['stop_ids'][-1]))
    total=0
    for line,meta in m['lines'].items():
        assert meta['file']==line.replace(':','-')+'.json'
        raw=(root/meta['file']).read_bytes();assert len(raw)==meta['bytes'] and len(raw)<=8_000_000 and hashlib.sha256(raw).hexdigest()==meta['sha256']
        package=json.loads(raw);validate_directions(package,m.get('directionVersion')==1);assert package['schemaVersion']==m['schemaVersion'] and package['lineId']==line and package['validFromUtc']==m['validFromUtc'] and package['validUntilUtc']==m['validUntilUtc']
        count=0
        for key,rows in package['groups'].items():
            stop,route,dest=json.loads(key);assert route==line and (stop,route,dest) in allowed and rows
            previous=None;identities=set()
            for row in rows:
                assert len(row)==(6 if m['schemaVersion']==2 else 4) and isinstance(row[0],int) and start.timestamp()<=row[0]<end.timestamp()
                assert previous is None or row>=previous
                dt.date.fromisoformat(row[1]);assert re.fullmatch('[a-f0-9]{16}',row[2]) and isinstance(row[3],int) and row[3]>=0
                if m['schemaVersion']==2:
                    assert (line,stop,row[4]) in next_edges and row[4] in bound and isinstance(row[5],int) and row[5]>row[3]
                    assert (stops[stop].get('parent_station') or stop)!=(stops[row[4]].get('parent_station') or row[4])
                identity=tuple(row);assert identity not in identities;identities.add(identity);previous=row;count+=1
        assert len(package['groups'])==meta['groups']==m['qa']['lines'][line]['groups'] and count==m['qa']['lines'][line]['departures'];total+=count
    return {'lines':len(expected),'places':len(places),'departures':total,'validUntilUtc':m['validUntilUtc']}

if __name__=='__main__':print('MOBILITY_VALID',json.dumps(check()))

