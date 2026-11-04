"""Independent geometric comparison: official GTFS shapes versus official rail network."""
import collections,hashlib,json,math,pathlib
ROOT=pathlib.Path('referentiel');CELL=.005;SEARCH_M=500;WARNING_M=100

def distance_to_edge(point,a,b):
    sx=111320*math.cos(math.radians(point[1]));ax=(a[0]-point[0])*sx;ay=(a[1]-point[1])*111320
    dx=(b[0]-a[0])*sx;dy=(b[1]-a[1])*111320;den=dx*dx+dy*dy
    t=max(0,min(1,-(ax*dx+ay*dy)/den)) if den else 0
    return math.hypot(ax+t*dx,ay+t*dy)

def main():
    rail_path=ROOT/'metro_service_segments.geojson';shape_path=ROOT/'gtfs/shapes.json'
    rail=json.loads(rail_path.read_text())['features'];shapes=json.loads(shape_path.read_text());patterns=json.loads((ROOT/'gtfs/patterns.json').read_text())
    grid=collections.defaultdict(list);routes=set()
    for feature in rail:
        route=feature['properties']['route_id'];routes.add(route);g=feature['geometry'];lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
        for line in lines:
            for a,b in zip(line,line[1:]):
                edge=(tuple(a[:2]),tuple(b[:2]))
                for x in range(math.floor(min(a[0],b[0])/CELL),math.floor(max(a[0],b[0])/CELL)+1):
                    for y in range(math.floor(min(a[1],b[1])/CELL),math.floor(max(a[1],b[1])/CELL)+1):grid[(route,x,y)].append(edge)
    shape_routes=collections.defaultdict(set)
    for p in patterns:shape_routes[p['shape_id']].add(p['route_id'])
    samples=collections.defaultdict(set)
    for shape in shapes:
        coords=shape['geometry']['coordinates']
        for a,b in zip(coords,coords[1:]):
            length=math.hypot((a[0]-b[0])*111320*math.cos(math.radians(a[1])),(a[1]-b[1])*111320);steps=max(1,math.ceil(length/100))
            for k in range(steps+1):
                p=(round(a[0]+(b[0]-a[0])*k/steps,7),round(a[1]+(b[1]-a[1])*k/steps,7))
                for route in shape_routes[shape['properties']['shape_id']]:samples[route].add(p)
    report=[]
    for route,points in sorted(samples.items()):
        distances=[];unmatched=0;above=0
        for point in points:
            dx=SEARCH_M/(111320*math.cos(math.radians(point[1])));dy=SEARCH_M/111320;edges=set()
            for x in range(math.floor((point[0]-dx)/CELL),math.floor((point[0]+dx)/CELL)+1):
                for y in range(math.floor((point[1]-dy)/CELL),math.floor((point[1]+dy)/CELL)+1):edges.update(grid.get((route,x,y),[]))
            nearest=min((distance_to_edge(point,*edge) for edge in edges),default=float('inf'))
            if nearest>SEARCH_M:unmatched+=1
            else:distances.append(nearest)
            if nearest>WARNING_M:above+=1
        distances.sort()
        report.append({'route_id':route,'sample_points':len(points),'known_distances':len(distances),
            'p50_known_m':round(distances[len(distances)//2],2) if distances else None,
            'p95_known_m':round(distances[min(len(distances)-1,int(len(distances)*.95))],2) if distances else None,
            'max_known_m':round(max(distances),2) if distances else None,
            'points_over_100m':above,'points_over_500m_or_unmatched':unmatched,'rail_route_present':route in routes})
    result={'kind':'independent-official-source-comparison-not-ground-truth','sampling_max_spacing_m':100,'search_radius_m':SEARCH_M,
        'rail_sha256':hashlib.sha256(rail_path.read_bytes()).hexdigest(),'gtfs_shapes_sha256':hashlib.sha256(shape_path.read_bytes()).hexdigest(),
        'routes':report,'total_sample_points':sum(r['sample_points'] for r in report),'points_over_100m':sum(r['points_over_100m'] for r in report),
        'points_over_500m_or_unmatched':sum(r['points_over_500m_or_unmatched'] for r in report),
        'limitation':'Distance between two reference datasets; not a GPS error measurement or proof of passenger service.'}
    (ROOT/'source_comparison_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='routes'},ensure_ascii=False))
if __name__=='__main__':main()

