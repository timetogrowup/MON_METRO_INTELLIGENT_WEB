"""Normalize official GTFS parent stations without joining stations by name."""
import collections, hashlib, json, pathlib
ROOT=pathlib.Path('referentiel')
def normalize(stops,patterns):
    points={s['stop_id']:s for s in stops};stations={};members=collections.defaultdict(set);normalized=[]
    def parent(s):return points[s].get('parent_station') or s
    for p in patterns:
        sequence=[]
        for sid in p['stop_ids']:
            station=parent(sid);source=points[station]
            if station not in stations:
                stations[station]={'id':station,'name':source['stop_name'],'lon':float(source['stop_lon']),
                    'lat':float(source['stop_lat']),'stop_point_ids':set(),'route_ids':set()}
            stations[station]['stop_point_ids'].add(sid);stations[station]['route_ids'].add(p['route_id'])
            members[sid].add(p['route_id'])
            if not sequence or sequence[-1]!=station:sequence.append(station)
        normalized.append({**p,'station_ids':sequence,'terminus_station_id':sequence[-1]})
    for s in stations.values():
        s['stop_point_ids']=sorted(s['stop_point_ids']);s['route_ids']=sorted(s['route_ids'])
    return sorted(stations.values(),key=lambda s:s['id']),normalized

def main():
    folder=ROOT/'gtfs';stops=json.loads((folder/'stops.json').read_text());patterns=json.loads((folder/'patterns.json').read_text())
    stations,patterns=normalize(stops,patterns)
    routes={r['route_id'] for r in json.loads((folder/'lines.json').read_text())}
    rail=json.loads((ROOT/'metro_segments.geojson').read_text())['features'];selected=[];excluded=[]
    for f in rail:
        p=f['properties'];rid='IDFM:'+str(p.get('idrefligc'))
        if rid not in routes:
            excluded.append({'source_id':p.get('objectid_1'),'line':p.get('indice_lig'),'reason':'not in GTFS services on reference date'})
            continue
        sid=hashlib.sha256(json.dumps([rid,f['geometry']],sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
        selected.append({'type':'Feature','geometry':f['geometry'],'properties':{'id':sid,'route_id':rid,
            'line':p.get('indice_lig'),'source_objectid':p.get('objectid_1'),'status':'line-geometry-not-station-edge'}})
    payloads={'stations_master':stations,'patterns_master':patterns,
        'metro_service_segments':{'type':'FeatureCollection','features':selected}}
    files={}
    for name,value in payloads.items():
        data=(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode()
        path=name+('.geojson' if name=='metro_service_segments' else '.json')
        (ROOT/path).write_bytes(data);files[path]={'sha256':hashlib.sha256(data).hexdigest()}
    report={'station_count':len(stations),'pattern_count':len(patterns),'service_geometry_count':len(selected),
        'excluded_rail_segments':excluded,'files':files,
        'status':'station order available; rail edges not spatially matched',
        'source_gtfs_manifest_sha256':hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest()}
    (ROOT/'master_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

