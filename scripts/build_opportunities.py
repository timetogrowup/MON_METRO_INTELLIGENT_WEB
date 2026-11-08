"""Build public, licensed POI snapshots; never query suppliers with a visitor's GPS."""
import argparse, csv, datetime as dt, gzip, hashlib, html, io, json, re, time
import urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ('food','events','walk','needs','sport','shop','work','sleep','health')
DATASET = 'https://www.data.gouv.fr/api/1/datasets/datatourisme-la-plateforme-nationale-des-donnees-touristiques/'
OSM_QUERY = '[out:json][timeout:120];area["ISO3166-2"="FR-IDF"]["boundary"="administrative"]->.a;(nwr(area.a)[amenity~"^(pharmacy|library|toilets|drinking_water|coworking_space)$"];nwr(area.a)[office=coworking];);out center tags;'
PARIS = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/'

def digest(raw): return hashlib.sha256(raw).hexdigest()
def compact(value): return json.dumps(value, ensure_ascii=False, separators=(',',':')).encode()
def text(value, limit=400):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', str(value or '')))).strip()[:limit]
def safe_url(value):
    try:
        u=urllib.parse.urlsplit(str(value or '').strip())
        return u.geturl() if u.scheme in ('https','http') and u.hostname and not u.username and not u.password else ''
    except ValueError: return ''
def download(url, timeout=60):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'WENARE-opportunities/1.0 (public snapshot builder)','Accept-Encoding':'identity'})
            with urllib.request.urlopen(req,timeout=timeout) as response: raw=response.read(40_000_001)
            if len(raw)>40_000_000: raise ValueError('Source exceeds bounded download')
            return gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw
        except (OSError, TimeoutError):
            if attempt==2: raise
            time.sleep(attempt+1)

def tourism_categories(types):
    t={x.rsplit('#',1)[-1] for x in types.split('|') if x.startswith('https://www.datatourisme.fr/ontology/core#')}
    result=[]
    if 'FoodEstablishment' in t: result.append('food')
    if 'EntertainmentAndEvent' in t: result.append('events')
    if t & {'ParkAndGarden','NaturalHeritage','RemarkableBuilding','Museum','CulturalSite','PanoramicView','WalkingTour'}: result.append('walk')
    if t & {'SwimmingPool','Stadium','SportsHall','Gymnasium','FitnessCenter','TennisComplex','MultiSportsGround','EquestrianCenter','GolfCourse','ClimbingWall','SportsClub','SportsField'}: result.append('sport')
    if t & {'Store','ServiceProvider','Market'}: result.append('shop')
    if t & {'Library','CoworkingSpace'}: result.append('work')
    if 'Accommodation' in t: result.append('sleep')
    return result

def periods(value):
    result=[]
    for part in value.split('|'):
        pair=part.split('<->')
        if len(pair)!=2: continue
        try: a,b=[dt.date.fromisoformat(p.strip()) for p in pair]
        except ValueError: continue
        # Some upstream ranges are reversed: reject, never silently swap them.
        if a<=b: result.append([str(a),str(b)])
    return result

def tourism_rows(raw):
    out=[]
    for row in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))):
        try: lat,lon=float(row['Latitude']),float(row['Longitude'])
        except (ValueError,KeyError): continue
        if not (48<=lat<=49.5 and 1.3<=lon<=3.7): continue
        name=text(row.get('Nom_du_POI'),160); identifier=safe_url(row.get('URI_ID_du_POI'))
        if not name or not identifier: continue
        contacts=row.get('Contacts_du_POI',''); website=next((safe_url(v) for v in re.split(r'[#|\s]',contacts) if safe_url(v)), '')
        for category in tourism_categories(row.get('Categories_de_POI','')):
            ranges=periods(row.get('Periodes_regroupees','')) if category=='events' else []
            if category=='events' and not ranges: continue
            out.append({'id':identifier,'category':category,'name':name,'lat':lat,'lon':lon,
                'address':text((row.get('Adresse_postale','')+' '+row.get('Code_postal_et_commune','').replace('#',' ')),240),
                'description':text(row.get('Description')),'source':'datatourisme','producer':text(row.get('Createur_de_la_donnee'),180),
                'modified':text(row.get('Date_de_mise_a_jour'),40),'url':website or identifier,
                'periods':ranges,'openingHours':'','access':'','fee':'','availability':'unknown','positionKind':'source'})
    return out

def osm_rows(payload):
    if payload.get('remark'): raise ValueError('Incomplete OSM response: '+payload['remark'])
    out=[]
    for row in payload.get('elements',[]):
        t=row.get('tags',{}); amenity=t.get('amenity'); center=row.get('center',row)
        if t.get('access') in ('private','no') or t.get('disused')=='yes': continue
        cat={'pharmacy':'health','library':'work','toilets':'needs','drinking_water':'needs','coworking_space':'work'}.get(amenity)
        if not cat and t.get('office')=='coworking': cat='work'
        if not cat or 'lat' not in center or 'lon' not in center: continue
        name=text(t.get('name') or {'toilets':'Toilettes publiques','drinking_water':"Point d’eau potable"}.get(amenity,''),160)
        if not name: continue
        # A tagged drinking fountain with an explicit negative potable status is excluded.
        if amenity=='drinking_water' and t.get('drinking_water')=='no': continue
        identifier='https://www.openstreetmap.org/'+row['type']+'/'+str(row['id'])
        out.append({'id':identifier,'category':cat,'name':name,'lat':center['lat'],'lon':center['lon'],
            'address':text(' '.join(t.get(k,'') for k in ['addr:housenumber','addr:street','addr:postcode','addr:city']),240),
            'description':'','source':'osm','producer':'© les contributeurs OpenStreetMap','modified':'',
            'url':safe_url(t.get('website') or t.get('contact:website')) or identifier,
            'periods':[],'openingHours':text(t.get('opening_hours'),250),'access':text(t.get('wheelchair'),40),
            'fee':text(t.get('fee'),50),'availability':'unknown','positionKind':'point' if row['type']=='node' else 'centroid'})
    return out

def paris_rows(name, rows):
    out=[]
    for row in rows:
        geo=row.get('geo_point_2d') or row.get('lat_lon') or {}
        if not isinstance(geo,dict) or not all(k in geo for k in ['lat','lon']): continue
        if name=='sanisettesparis':
            if row.get('statut')!='En service': continue
            title='Toilettes · '+text(row.get('adresse'),100); ident='sanisette:'+str(row.get('adresse'))+':'+str(geo['lat'])+':'+str(geo['lon'])
            hours=text(row.get('horaire'),250); address=text(row.get('adresse')); access='yes' if row.get('acces_pmr')=='Oui' else ''
        else:
            if row.get('dispo')!='OUI': continue
            title='Fontaine · '+text(row.get('voie'),100);ident='fontaine:'+str(row.get('gid'))
            hours='';address=text(' '.join(str(row.get(k) or '') for k in ['no_voirie_pair','voie','commune']));access=''
        out.append({'id':ident,'category':'needs','name':title,'lat':geo['lat'],'lon':geo['lon'],'address':address,
            'description':'État déclaré par la source, sans contrôle en temps réel.','source':'paris','producer':'Ville de Paris / Eau de Paris',
            'modified':'','url':safe_url(row.get('url_fiche_equipement')) or 'https://opendata.paris.fr/explore/dataset/'+name+'/',
            'periods':[],'openingHours':hours,'access':access,'fee':'','availability':'declared-in-service','positionKind':'point'})
    return out

def validate(entries):
    ids=set()
    for p in entries:
        key=(p['category'],p['id'])
        if key in ids: raise ValueError('Duplicate source identity')
        ids.add(key)
        if p['category'] not in CATEGORIES or not p['name'] or len(p['name'])>160: raise ValueError('Invalid identity')
        if not(48<=p['lat']<=49.5 and 1.3<=p['lon']<=3.7): raise ValueError('Invalid IDF coordinates')
        if p['availability'] not in ('unknown','declared-in-service'): raise ValueError('Unproven availability')
        if not safe_url(p['url']): raise ValueError('Unsafe URL')
    return True

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-dir',type=Path);args=parser.parse_args()
    cache=args.source_dir or ROOT/'.cache'/'opportunities';cache.mkdir(parents=True,exist_ok=True)
    if not args.source_dir:
        data=json.loads(download(DATASET));resource=next(r for r in data['resources'] if r['title']=='datatourisme-reg-idf.csv')
        if data.get('license') not in ('fr-lo','etalab-2.0'):raise ValueError('Tourism license changed')
        (cache/'datatourisme-idf.csv').write_bytes(download(resource['url']))
        (cache/'datatourisme-meta.json').write_text(json.dumps({'url':resource['url'],'modified':resource['last_modified'],'license':data['license'],'resource':resource['id']}))
        osm_url='https://overpass-api.de/api/interpreter?'+urllib.parse.urlencode({'data':OSM_QUERY})
        (cache/'osm-idf.json').write_bytes(download(osm_url,150))
    now=dt.datetime.now(dt.timezone.utc);collected=now.isoformat();raw=(cache/'datatourisme-idf.csv').read_bytes();meta=json.loads((cache/'datatourisme-meta.json').read_text())
    entries=tourism_rows(raw)+osm_rows(json.loads((cache/'osm-idf.json').read_bytes()))
    sources={
      'datatourisme':{'name':'DATAtourisme — producteurs touristiques territoriaux','license':'Licence Ouverte 2.0','licenseUrl':'https://www.etalab.gouv.fr/licence-ouverte-open-licence/','url':meta['url'],'modified':meta['modified'],'sha256':digest(raw),'coverage':'Île-de-France, couverture touristique partielle'},
      'osm':{'name':'© les contributeurs OpenStreetMap','license':'ODbL 1.0','licenseUrl':'https://www.openstreetmap.org/copyright','url':'https://www.openstreetmap.org','sha256':digest((cache/'osm-idf.json').read_bytes()),'coverage':'Île-de-France, saisie contributive partielle'},
      'paris':{'name':'Ville de Paris / Eau de Paris','license':'ODbL 1.0','licenseUrl':'https://opendata.paris.fr/pages/conditions-generales-dutilisation/','url':'https://opendata.paris.fr/','coverage':'Paris uniquement, équipements déclarés en service'}
    }
    # A missing optional local enrichment never corrupts the regional sources.
    issues=[]
    for name in ('sanisettesparis','fontaines-a-boire'):
        path=cache/(name+'.json')
        try:
            if not args.source_dir or not path.exists():
                info=json.loads(download(PARIS+name));license_name=info.get('metas',{}).get('default',{}).get('license','')
                if license_name!='Open Database License (ODbL)': raise ValueError('Paris license changed')
                path.write_bytes(download(PARIS+name+'/exports/json'))
            raw=path.read_bytes();rows=json.loads(raw);entries+=paris_rows(name,rows)
            sources['paris'][name+'Sha256']=digest(raw)
        except (OSError,ValueError,KeyError) as e:issues.append(name+': '+type(e).__name__)
    unique={}
    duplicate_count=0
    for item in entries:
        key=(item['category'],item['id'])
        if key in unique:
            previous=unique[key]
            if previous['name']!=item['name'] or abs(previous['lat']-item['lat'])>0.001 or abs(previous['lon']-item['lon'])>0.001:
                raise ValueError('Conflicting source identity: '+item['id'])
            previous['periods']=sorted({tuple(r) for r in previous['periods']+item['periods']})
            previous['periods']=[list(r) for r in previous['periods']]
            duplicate_count+=1
        else:unique[key]=item
    entries=list(unique.values())
    validate(entries)
    target=ROOT/'distribution'/'opportunities';target.mkdir(parents=True,exist_ok=True)
    manifest={'schemaVersion':1,'collectedAt':collected,'validUntilUtc':(now+dt.timedelta(days=7)).isoformat(),'sources':sources,
        'limits':'Référentiel partiel ; aucune place, garde, réservation ou ouverture en temps réel garantie. Les dates de collecte ne remplacent pas la date de vérification de chaque fiche.',
        'issues':issues,'duplicateSourceRows':duplicate_count,'categories':{},'license':'Collective database: ODbL 1.0; DATAtourisme records retain Licence Ouverte 2.0 and their attribution.'}
    total=0
    for cat in CATEGORIES:
        records=sorted([p for p in entries if p['category']==cat],key=lambda p:p['id'])
        if not records:raise ValueError('Unpopulated required category: '+cat)
        blob=compact({'schemaVersion':1,'category':cat,'items':records});(target/(cat+'.json')).write_bytes(blob);total+=len(records)
        manifest['categories'][cat]={'file':cat+'.json','count':len(records),'bytes':len(blob),'sha256':digest(blob)}
    (target/'manifest.json').write_bytes(compact(manifest));print(json.dumps({'status':'OPPORTUNITIES_VALIDATED','total':total,'categories':{k:v['count'] for k,v in manifest['categories'].items()},'issues':issues}))

if __name__=='__main__': main()
