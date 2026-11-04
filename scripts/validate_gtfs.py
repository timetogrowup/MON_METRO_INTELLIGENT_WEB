"""Cross-source ID audit; preserve differences instead of fuzzy-name joins."""
import collections, hashlib, json, pathlib
ROOT=pathlib.Path('referentiel')

def main():
    folder=ROOT/'gtfs';manifest=json.loads((folder/'manifest.json').read_text());data={}
    for name,info in manifest['files'].items():
        raw=(folder/(name+'.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=info['sha256']:raise ValueError(f'GTFS hash mismatch: {name}')
        data[name]=json.loads(raw)
        if len(data[name])!=info['count']:raise ValueError('GTFS count mismatch')
    stops={s['stop_id']:s for s in data['stops']};lines={r['route_id']:r for r in data['lines']}
    used=set();degrees=collections.defaultdict(set)
    for p in data['patterns']:
        if p['route_id'] not in lines or len(p['stop_ids'])<2:raise ValueError('Invalid pattern')
        for s in p['stop_ids']:
            if s not in stops:raise ValueError('Unknown pattern stop')
            used.add((p['route_id'],s))
        for a,b in zip(p['stop_ids'],p['stop_ids'][1:]):degrees[(p['route_id'],a)].add(b)
    source=json.loads((ROOT/'station_associations.json').read_text())['associations']
    associations={(r['id'],r['stop_id']) for r in source}
    missing=sorted(used-associations);inactive=sorted(associations-used)
    expected={'1','2','3','3bis','4','5','6','7','7bis','8','9','10','11','12','13','14'}
    declared=data['lines']+data.get('inactive_lines',[])
    actual={r.get('route_short_name','').replace(' ','').lower() for r in declared}
    actual={ {'3b':'3bis','7b':'7bis'}.get(x,x) for x in actual}
    missing_lines=sorted(expected-actual)
    if missing_lines:raise ValueError(f'Missing expected metro lines: {missing_lines}')
    shapes={s['properties']['shape_id'] for s in data.get('shapes',[])}
    report={'service_date':manifest['service_date'],'line_count':len(lines),'declared_inactive_lines':data.get('inactive_lines',[]),'stop_points':len({s for _,s in used}),
            'station_parents':len({s.get('parent_station') for s in stops.values()}-{None,''}),
            'pattern_count':len(data['patterns']),'directed_edges':len(data['edges']),
            'branch_nodes':[{'route_id':r,'stop_id':s,'next_stop_ids':sorted(v)} for (r,s),v in degrees.items() if len(v)>1],
            'gtfs_associations_absent_from_station_source':missing,'station_associations_not_active_today':inactive,
            'patterns_without_loaded_shape':[p['id'] for p in data['patterns'] if p.get('shape_id') not in shapes],
            'coverage_status':'IDs compared; divergences require review',
            'spatial_rail_matching':'not performed','field_validation':'not performed'}
    (folder/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},ensure_ascii=False))
if __name__=='__main__':main()

