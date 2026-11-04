import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_master import normalize
class Master(unittest.TestCase):
    def test_parent_ids_and_interchange(self):
        stops=[{'stop_id':'A','parent_station':'S','stop_name':'Platform A','stop_lon':'2.3','stop_lat':'48.8'},
            {'stop_id':'B','parent_station':'S','stop_name':'Platform B','stop_lon':'2.3','stop_lat':'48.8'},
            {'stop_id':'S','parent_station':'','stop_name':'Station','stop_lon':'2.3','stop_lat':'48.8'},
            {'stop_id':'T','parent_station':'','stop_name':'Station','stop_lon':'2.4','stop_lat':'48.9'}]
        stations,patterns=normalize(stops,[{'route_id':'1','stop_ids':['A','T']},{'route_id':'2','stop_ids':['B','T']}])
        self.assertEqual(len(stations),2) # equal names must never merge different IDs
        self.assertEqual(stations[0]['route_ids'],['1','2'])
        self.assertEqual(patterns[0]['station_ids'],['S','T'])
if __name__=='__main__':unittest.main()

