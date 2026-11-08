import csv,datetime as dt,io,json,pathlib,sys,unittest,zipfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from build_timetable import trip_direction,validate_directions
from build_mobility import build
import test_mobility
class SourceDirections(unittest.TestCase):
 def test_source_values_are_not_inferred(self):
  self.assertEqual(trip_direction({'direction_id':'0'}),'0');self.assertEqual(trip_direction({'direction_id':'1'}),'1');self.assertIsNone(trip_direction({}));self.assertIsNone(trip_direction({'direction_id':''}))
  with self.assertRaises(ValueError):trip_direction({'direction_id':'2'})
 def test_bus_and_rer_builder_preserves_source_per_trip(self):
  fixture=test_mobility.Mobility();memory=io.BytesIO();expected={}
  with fixture.archive() as original,zipfile.ZipFile(memory,'w') as out:
   for name in original.namelist():
    raw=original.read(name)
    if name=='trips.txt':
     rows=list(csv.DictReader(io.StringIO(raw.decode())));text=io.StringIO();writer=csv.DictWriter(text,fieldnames=[*rows[0],'direction_id']);writer.writeheader()
     for i,row in enumerate(rows):row['direction_id']=str(i%2);expected['IDFM:'+row['trip_id']]=row['direction_id'];writer.writerow(row)
     raw=text.getvalue().encode()
    out.writestr(name,raw)
  with zipfile.ZipFile(memory) as z:index,packages,qa=build(z,fixture.reference(),dt.date(2026,11,3))
  for line,payload in packages.items():validate_directions(payload,True);self.assertEqual(set(payload['tripDirections'].values()),{expected[line]})
 def test_missing_or_corrupt_direction_bindings_are_rejected(self):
  data={'directionVersion':1,'tripDirections':{'t':'0'},'groups':{'k':[[1,'date','t']]}};validate_directions(data,True)
  for directions in [{},{'t':'2'},{'t':'0','unused':'1'}]:
   with self.assertRaises(AssertionError):validate_directions({**data,'tripDirections':directions},True)
