"""Match ordered GTFS stop points to their own trip shape; report all failures."""
import hashlib,json,math,pathlib
ROOT=pathlib.Path('referentiel')
def project(point,line,tolerance=200):
    candidates=[];lat=math.radians(point[1]);sx=111320*math.cos(lat);sy=111320
    for i,(a,b) in enumerate(zip(line,line[1:])):
        ax=(a[0]-point[0])*sx;ay=(a[1]-point[1])*sy
        dx=(b[0]-a[0])*sx;dy=(b[1]-a[1])*sy
        den=dx*dx+dy*dy
        if den==0:continue
        t=max(0,min(1,-(ax*dx+ay*dy)/den));distance=math.hypot(ax+t*dx,ay+t*dy)
        if distance<=tolerance:candidates.append((i+t,distance,[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]))
    return candidates

def align(points,line):
    layers=[]
    for point in points:
        candidates=project(point,line)
        if not candidates:raise ValueError('Stop farther than 200m from official trip shape')
        layer=[]
        for pos,distance,xy in candidates:
            if not layers:layer.append((distance**2,None,pos,distance,xy));continue
            previous=[(v[0],i) for i,v in enumerate(layers[-1]) if v[2]+1e-6<pos]
            if previous:
                cost,index=min(previous);layer.append((cost+distance**2,index,pos,distance,xy))
        if not layer:raise ValueError('No monotonic stop/shape alignment')
        layers.append(layer)
    index=min(range(len(layers[-1])),key=lambda i:layers[-1][i][0]);result=[]
    for layer in reversed(layers):
        value=layer[index];result.append(value);index=value[1]
    return list(reversed(result))

def main():
    folder=ROOT/'gtfs';patterns=json.loads((folder/'patterns.json').read_text());stops={s['stop_id']:s for s in json.loads((folder/'stops.json').read_text())}
    shapes={s['properties']['shape_id']:s['geometry']['coordinates'] for s in json.loads((folder/'shapes.json').read_text())}
    features=[];errors=[];max_distance=0
    for p in patterns:
        try:
            line=shapes[p['shape_id']]
            points=[[float(stops[s]['stop_lon']),float(stops[s]['stop_lat'])] for s in p['stop_ids']]
            matched=align(points,line)
            max_distance=max(max_distance,max(x[3] for x in matched))
            for i,(a,b) in enumerate(zip(matched,matched[1:])):
                coordinates=[a[4]]+[line[k] for k in range(math.floor(a[2])+1,math.ceil(b[2]))]+[b[4]]
                coordinates=[v for k,v in enumerate(coordinates) if not k or v!=coordinates[k-1]]
                features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':coordinates},
                    'properties':{'id':p['id']+':'+str(i),'pattern_id':p['id'],'route_id':p['route_id'],
                        'from_stop_id':p['stop_ids'][i],'to_stop_id':p['stop_ids'][i+1],
                        'sequence':i,'max_endpoint_offset_m':round(max(a[3],b[3]),2),
                        'source':'official GTFS trip shape','status':'geometric-alignment-not-field-validated'}})
        except (KeyError,ValueError) as exc:errors.append({'pattern_id':p['id'],'error':str(exc)})
    payload=(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n').encode()
    (ROOT/'directed_segments.geojson').write_bytes(payload)
    report={'patterns':len(patterns),'matched_patterns':len(patterns)-len(errors),'unmatched_patterns':errors,
        'directed_pattern_segments':len(features),'max_endpoint_offset_m':max_distance,'tolerance_m':200,
        'sha256':hashlib.sha256(payload).hexdigest(),'status':'complete' if not errors else 'partial-do-not-publish-as-complete',
        'limitation':'Alignment to own GTFS shape; independent comparison with rail source and field checks remain required.'}
    (ROOT/'shape_matching_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

