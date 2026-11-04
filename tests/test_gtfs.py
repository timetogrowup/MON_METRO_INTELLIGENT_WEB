import datetime,io,sys,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_gtfs import build
class GTFS(unittest.TestCase):
    def test_modes_dates_and_sequences(self):
        fixture={'calendar_dates':'service_id,date,exception_type\ns,20261103,1\n',
         'routes':'route_id,route_type\nm,1\nb,3\nn,1\n',
         'trips':'route_id,service_id,trip_id,direction_id\nm,s,t,0\nb,s,b,0\nm,other,x,1\nn,other,n,0\n',
         'stop_times':'trip_id,stop_id,stop_sequence\nt,B,2\nt,A,1\nb,C,1\nx,C,1\n',
         'stops':'stop_id,stop_name,stop_lon,stop_lat,parent_station\nA,Alpha,2.3,48.8,P\nB,Beta,2.4,48.9,P\nP,Parent,2.3,48.8,\nC,Bus,2.5,48.8,\n'}
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:
            for name,content in fixture.items():z.writestr(name+'.txt',content)
        data.seek(0)
        with zipfile.ZipFile(data) as z:r=build(z,datetime.date(2026,11,3))
        self.assertEqual(r['patterns'][0]['stop_ids'],('A','B'))
        self.assertEqual(r['edges'],[{'route_id':'m','from_stop_id':'A','to_stop_id':'B'}])
        self.assertEqual(len(r['lines']),1)
        self.assertEqual([line['route_id'] for line in r['inactive_lines']],['n'])
        self.assertEqual({s['stop_id'] for s in r['stops']},{'A','B','P'})
if __name__=='__main__':unittest.main()

