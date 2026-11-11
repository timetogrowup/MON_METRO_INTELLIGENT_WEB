import datetime as dt
import io
import pathlib
import sys
import unittest
import zipfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from build_timetable import build

class QualifiedFuturePatterns(unittest.TestCase):
    def test_future_variant_cannot_introduce_unqualified_hops(self):
        content=io.BytesIO()
        with zipfile.ZipFile(content,'w') as z:
            z.writestr('agency.txt','agency_id,agency_timezone\na,Europe/Paris\n')
            z.writestr('routes.txt','route_id,agency_id\nmetro,a\n')
            z.writestr('trips.txt','trip_id,route_id,service_id,direction_id\ngood,metro,normal,0\nvariant,metro,change,0\n')
            z.writestr('calendar_dates.txt','service_id,date,exception_type\n'+''.join('normal,202611%02d,1\n'%day for day in range(3,7))+'change,20261104,1\n')
            z.writestr('stop_times.txt','trip_id,stop_sequence,stop_id,departure_time,pickup_type\ngood,1,s,12:00:00,0\ngood,2,d,12:10:00,1\nvariant,1,s,13:00:00,0\nvariant,2,x,13:05:00,0\nvariant,3,d,13:10:00,1\n')
        network={'lines':[{'route_id':'metro','route_type':'1'}],'patterns':[{'route_id':'metro','stop_ids':['s','d']}],'stops':[{'stop_id':key} for key in ['s','x','d']]}
        with zipfile.ZipFile(content) as z: result,qa=build(z,network,dt.date(2026,11,3))
        rows=[row for group in result['metro']['groups'].values() for row in group]
        self.assertEqual(len(rows),4)
        self.assertEqual({row[4] for row in rows},{'d'})
        self.assertEqual(qa['unmatched_reference_events'],2)
        self.assertEqual(result['metro']['validUntilUtc'],'2026-11-06T23:00:00+00:00')
if __name__=='__main__':unittest.main()
