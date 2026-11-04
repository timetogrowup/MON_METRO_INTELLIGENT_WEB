"""Offline quality gate. Errors block commits; warnings never imply active service."""
import collections, hashlib, json, math
from pathlib import Path

def validate_geometry(geometry):
    kind = geometry.get('type')
    if kind not in ('LineString', 'MultiLineString'):
        raise ValueError('Non linear geometry')
    lines = [geometry['coordinates']] if kind == 'LineString' else geometry['coordinates']
    if not lines:
        raise ValueError('Empty geometry')
    for line in lines:
        if len(line) < 2:
            raise ValueError('Short line')
        for p in line:
            if len(p) < 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in p[:2]):
                raise ValueError('Invalid coordinate')
            if not (1 < p[0] < 4 and 48 < p[1] < 50):
                raise ValueError('Coordinate outside IDF bounds')
        if len({tuple(p[:2]) for p in line}) < 2:
            raise ValueError('Zero length line')

def check(root=Path('referentiel')):
    raw = (root / 'metro_segments.geojson').read_bytes()
    manifest = json.loads((root / 'metro_manifest.json').read_text())
    if hashlib.sha256(raw).hexdigest() != manifest['sha256']:
        raise ValueError('Metro hash mismatch')
    features = json.loads(raw)['features']
    if len(features) != manifest['metro_features']:
        raise ValueError('Metro count mismatch')
    lines, ids, geometries = collections.Counter(), collections.Counter(), collections.Counter()
    for f in features:
        p = f['properties']
        if p.get('metro') not in (1, True, '1') or p.get('mode') != 'METRO':
            raise ValueError('Inconsistent metro mode')
        validate_geometry(f['geometry'])
        lines[str(p.get('indice_lig'))] += 1
        ids[str(p.get('objectid_1'))] += 1
        geometries[json.dumps(f['geometry'], sort_keys=True)] += 1
    duplicates = {k:v for k,v in ids.items() if v > 1}
    if 'None' in ids:
        raise ValueError('Missing source identifiers')
    source = root / 'rail_segments_raw.geojson'
    if source.exists():
        source_bytes = source.read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != manifest['source_sha256']:
            raise ValueError('Raw source hash mismatch')
        expected = [f for f in json.loads(source_bytes)['features'] if f['properties'].get('metro') in (1, True, '1')]
        if expected != features:
            raise ValueError('Metro subset differs from source')
    return {'metro_features':len(features), 'lines':dict(sorted(lines.items())), 'source_ids_unique':not bool(duplicates), 'duplicate_source_ids':duplicates,
            'identical_feature_duplicates':len(features)-len({json.dumps(f,sort_keys=True) for f in features}),
            'duplicate_geometries':sum(v-1 for v in geometries.values()),
            'source_subset_checked':source.exists(), 'status':'geometry-only',
            'warnings':['Source line presence is not proof of active passenger service; validate against official GTFS.',
                        'Station coverage and topology not validated.']}

if __name__ == '__main__':
    report = check()
    Path('referentiel/metro_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

