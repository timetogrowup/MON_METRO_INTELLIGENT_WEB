"""Package only qualified official reference data, with byte-level integrity."""
import datetime,hashlib,json,pathlib
ROOT=pathlib.Path('referentiel');OUT=pathlib.Path('distribution')
def main():
    qa=json.loads((ROOT/'shape_matching_qa.json').read_text())
    coverage=json.loads((ROOT/'gtfs/qa.json').read_text())
    if qa['unmatched_patterns'] or coverage['gtfs_associations_absent_from_station_source']:
        raise ValueError('Incomplete reference must not be distributed')
    gtfs=json.loads((ROOT/'gtfs/manifest.json').read_text())
    value={'schema_version':1,'service_date':gtfs['service_date'],
        'stations':json.loads((ROOT/'stations_master.json').read_text()),
        'patterns':json.loads((ROOT/'patterns_master.json').read_text()),
        'lines':json.loads((ROOT/'gtfs/lines.json').read_text()),
        'stops':json.loads((ROOT/'gtfs/stops.json').read_text()),
        'segments':json.loads((ROOT/'directed_segments.geojson').read_text())['features'],
        'attribution':'Île-de-France Mobilités — données GTFS et arrêts/lignes — ODbL',
        'license_url':'https://opendatacommons.org/licenses/odbl/1-0/',
        'limitations':['Service théorique du jour indiqué ; aucune position de rame temps réel.',
                        'Géométrie appariée aux formes GTFS ; précision terrain non validée.']}
    encoded=(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode();sha=hashlib.sha256(encoded).hexdigest()
    manifest={'schema_version':1,'version':sha[:24],'sha256':sha,'bytes':len(encoded),'file':'network.json',
        'service_date':gtfs['service_date'],'counts':{k:len(value[k]) for k in ('stations','patterns','lines','stops','segments')},
        'source_gtfs_sha256':gtfs['source_sha256'],'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    OUT.mkdir(exist_ok=True);(OUT/'network.json').write_bytes(encoded);(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest))
if __name__=='__main__':main()

