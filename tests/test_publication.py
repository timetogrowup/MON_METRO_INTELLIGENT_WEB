import copy,datetime,hashlib,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_publication import validate,paris_day
class Publication(unittest.TestCase):
    def fixture(self):
        data={'schema_version':1,'service_date':'2026-11-03','stations':[{'id':'S','stop_point_ids':['A','B'],'route_ids':['L']}],
        'lines':[{'route_id':'L'}],'stops':[{'stop_id':'A','stop_lon':'2.3','stop_lat':'48.8'},{'stop_id':'B','stop_lon':'2.31','stop_lat':'48.8'}],
        'patterns':[{'id':'P','route_id':'L','stop_ids':['A','B'],'station_ids':['S']}],
        'segments':[{'type':'Feature','properties':{'id':'X','pattern_id':'P','sequence':0,'route_id':'L','from_stop_id':'A','to_stop_id':'B'},'geometry':{'type':'LineString','coordinates':[[2.3,48.8],[2.31,48.8]]}}]}
        return data
    def run_data(self,data,day='2026-11-03'):
        raw=json.dumps(data).encode();sha=hashlib.sha256(raw).hexdigest();m={'schema_version':1,'file':'network.json','sha256':sha,'version':sha[:24],'bytes':len(raw),'service_date':data['service_date'],'source_gtfs_sha256':'a'*64,'counts':{k:len(data[k]) for k in ['stations','lines','stops','patterns','segments']}}
        return validate(raw,m,datetime.date.fromisoformat(day))
    def test_valid(self):self.assertEqual(self.run_data(self.fixture())['status'],'validated-for-two-file-publication')
    def test_old_date(self):
        with self.assertRaises(ValueError):self.run_data(self.fixture(),'2026-11-04')
    def test_topology_and_geometry(self):
        for field,value in [('to_stop_id','missing'),('sequence',1),('pattern_id','missing')]:
            d=self.fixture();d['segments'][0]['properties'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.run_data(d)
        d=self.fixture();d['segments'][0]['geometry']['coordinates']=[[48.8,2.3],[48.8,2.31]]
        with self.assertRaises(ValueError):self.run_data(d)
    def test_missing_segment(self):
        d=self.fixture();d['patterns'][0]['stop_ids'].append('A')
        with self.assertRaises(ValueError):self.run_data(d)
    def test_paris_midnight(self):
        self.assertEqual(str(paris_day(datetime.datetime(2026,11,3,23,30,tzinfo=datetime.timezone.utc))),'2026-11-04')
        self.assertEqual(str(paris_day(datetime.datetime(2026,7,3,22,30,tzinfo=datetime.timezone.utc))),'2026-07-04')
if __name__=='__main__':unittest.main()

