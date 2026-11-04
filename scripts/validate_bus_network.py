"""Closed regional contract: official scope, provenance, bindings, dates and hashes."""
import datetime as dt, hashlib, json, pathlib, re
from build_bus_network import INDEX_LIMIT
from build_mobility import classify, LINE_URL
from build_gtfs import URL

def check(root=pathlib.Path('distribution/mobility'),now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    m=json.loads((root/'manifest.json').read_bytes());raw=(root/'index.json').read_bytes();d=json.loads(raw)
    assert m['schemaVersion']==2 and m['catalogueVersion']==3 and m['quality']=='timetable'
    assert m['source']==URL and m['lineSource']==LINE_URL
    assert re.fullmatch('[a-f0-9]{64}',m['sourceSha256']) and re.fullmatch('[a-f0-9]{64}',m['lineSourceSha256'])
    source=(root/'lines-source.json').read_bytes();assert hashlib.sha256(source).hexdigest()==m['lineSourceSha256']
    expected=classify(json.loads(source),all_bus=True)
    assert m['scope']=={k.removeprefix('IDFM:'):v['mode'] for k,v in expected.items()}
    start=dt.datetime.fromisoformat(m['validFromUtc']);end=dt.datetime.fromisoformat(m['validUntilUtc']);generated=dt.datetime.fromisoformat(m['generatedAtUtc'])
    assert start<=now<end and 0<=(now-generated).total_seconds()<172800 and 0<(end-start).total_seconds()<=49*3600
    assert m['index']['file']=='index.json' and len(raw)==m['index']['bytes'] and 0<len(raw)<=INDEX_LIMIT
    assert hashlib.sha256(raw).hexdigest()==m['index']['sha256']==m['networkSha256']
    assert d['schemaVersion']==3 and d['kind']=='consultation-only' and d['service_date']==m['referenceDate']
    assert d['validFromUtc']==m['validFromUtc'] and d['validUntilUtc']==m['validUntilUtc']
    assert {l['route_id']:l for l in d['lines']}==expected and len(d['lines'])==len(expected) and set(m['lines'])==set(expected)
    stops={s[0]:s for s in d['packed']['stops']};assert len(stops)==len(d['packed']['stops'])
    assert all(len(s)==4 and s[0] and s[1] for s in stops.values())
    places=set();bound=set()
    for s in d['packed']['stations']:
        assert len(s)==5 and s[0] not in places and s[0] in stops and s[1] and 47<s[2]<51 and 0<s[3]<6 and s[4];places.add(s[0])
        for p in s[4]:assert p in stops and p not in bound and (stops[p][2] or p)==s[0];bound.add(p)
    allowed={tuple(s) for s in d['packed']['services']};assert len(allowed)==len(d['packed']['services'])
    for s,line,dest in allowed:assert s in bound and dest in bound and line in expected
    assert set(d['coverage'])==set(expected)
    total=0;actual=set();coverage={}
    for line,meta in m['lines'].items():
        assert meta['file']==line.replace(':','-')+'.json'
        b=(root/meta['file']).read_bytes();assert len(b)==meta['bytes'] and len(b)<=8_000_000 and hashlib.sha256(b).hexdigest()==meta['sha256']
        p=json.loads(b);assert p['schemaVersion']==2 and p['lineId']==line and p['validFromUtc']==m['validFromUtc'] and p['validUntilUtc']==m['validUntilUtc']
        state=d['coverage'][line];assert state in ('dated_departures','no_dated_departures','absent_from_gtfs')
        assert bool(p['groups'])==(state=='dated_departures');coverage[state]=coverage.get(state,0)+1
        count=0
        for key,rows in p['groups'].items():
            stop,route,dest=json.loads(key);assert route==line and (stop,route,dest) in allowed and rows;actual.add((stop,route,dest))
            previous=None;identities=set()
            for row in rows:
                assert len(row)==6 and isinstance(row[0],int) and start.timestamp()<=row[0]<end.timestamp()
                assert previous is None or row>=previous
                dt.date.fromisoformat(row[1]);assert re.fullmatch('[a-f0-9]{16}',row[2]) and isinstance(row[3],int) and row[3]>=0
                assert row[4] in bound and isinstance(row[5],int) and row[5]>row[3]
                assert (stops[stop][2] or stop)!=(stops[row[4]][2] or row[4])
                identity=tuple(row);assert identity not in identities;identities.add(identity);previous=row;count+=1
        assert len(p['groups'])==meta['groups']==m['qa']['lines'][line]['groups'] and count==m['qa']['lines'][line]['departures'];total+=count
    assert actual==allowed and coverage==m['qa']['coverage']
    assert m['qa']['busLines']==sum(v['mode']=='bus' for v in expected.values())
    return {'lines':len(expected),'busLines':m['qa']['busLines'],'places':len(places),'departures':total,'coverage':coverage,'indexBytes':len(raw),'validUntilUtc':m['validUntilUtc']}
if __name__=='__main__':print('BUS_IDF_VALID',json.dumps(check()))
