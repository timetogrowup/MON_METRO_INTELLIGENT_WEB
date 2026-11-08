import csv,io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_opportunities import tourism_categories,periods,osm_rows,paris_rows,safe_url,text
class Opportunities(unittest.TestCase):
    def test_categories(self):
        prefix='https://www.datatourisme.fr/ontology/core#'
        self.assertEqual(tourism_categories(prefix+'Hotel|'+prefix+'Accommodation'),['sleep'])
        self.assertEqual(tourism_categories(prefix+'Cinema'),[])
        self.assertEqual(tourism_categories(prefix+'SwimmingPool'),['sport'])
    def test_reversed_dates_rejected(self):
        self.assertEqual(periods('2026-11-08<->2026-04-18'),[])
        self.assertEqual(periods('2026-11-08<->2026-11-09'),[['2026-11-08','2026-11-09']])
    def test_markup_and_url(self):
        self.assertEqual(text('<b>Lieu</b> &amp; parc'),'Lieu & parc')
        self.assertEqual(safe_url('javascript:alert(1)'),'')
        self.assertEqual(safe_url('https://a:b@example.org'),'')
    def test_private_access_and_nonpotable_excluded(self):
        base={'id':1,'type':'node','lat':48.85,'lon':2.35,'tags':{'amenity':'toilets'}}
        self.assertEqual(len(osm_rows({'elements':[base]})),1)
        base['tags']['access']='private';self.assertEqual(osm_rows({'elements':[base]}),[])
        base['tags']={'amenity':'drinking_water','drinking_water':'no'};self.assertEqual(osm_rows({'elements':[base]}),[])
        with self.assertRaises(ValueError):osm_rows({'remark':'runtime timeout','elements':[]})
    def test_closed_equipment_and_distinct_coordinates(self):
        r={'geo_point_2d':{'lat':48.85,'lon':2.35},'statut':'Hors service','adresse':'Rue'}
        self.assertEqual(paris_rows('sanisettesparis',[r]),[])
        r['statut']='En service';other={**r,'geo_point_2d':{'lat':48.86,'lon':2.35}}
        rows=paris_rows('sanisettesparis',[r,other]);self.assertNotEqual(rows[0]['id'],rows[1]['id'])
if __name__=='__main__':unittest.main()
