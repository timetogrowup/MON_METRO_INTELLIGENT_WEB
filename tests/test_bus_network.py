import datetime as dt,sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import test_mobility
from build_mobility import classify,build
from build_bus_network import compact
class Regional(unittest.TestCase):
 def test_all_active_buses_selected_by_id_even_duplicate_names(self):
  rows=test_mobility.Mobility().reference();extra=dict(rows[-1],id_line='C99998',name_line='20');rows.append(extra)
  rows.append(dict(extra,id_line='C99997',status='prochainement active'))
  rows.append(dict(extra,id_line='C99996',transportmode='tram'))
  selected=classify(rows,all_bus=True)
  self.assertEqual(selected['IDFM:C99998']['mode'],'bus');self.assertNotIn('IDFM:C99997',selected);self.assertNotIn('IDFM:C99996',selected)
  self.assertEqual(selected['IDFM:C01072']['route_short_name'],selected['IDFM:C99998']['route_short_name'])
 def test_unavailable_official_line_is_catalogued_without_invented_departures(self):
  fixture=test_mobility.Mobility();rows=fixture.reference();rows.append(dict(rows[-1],id_line='C99998',name_line='20'))
  with fixture.archive() as z:index,packages,qa=build(z,rows,dt.date(2026,11,3),all_bus=True)
  self.assertEqual(packages['IDFM:C99998']['groups'],{});self.assertEqual(qa['lines']['IDFM:C99998']['departures'],0)
  packed=compact(index,packages);self.assertFalse(any(s[1]=='IDFM:C99998' for s in packed['packed']['services']))
 def test_frequency_only_lines_stay_without_exact_countdown(self):
  fixture=test_mobility.Mobility()
  with fixture.archive(True) as z:index,packages,qa=build(z,fixture.reference(),dt.date(2026,11,3),all_bus=True)
  self.assertTrue(any(not p['groups'] for p in packages.values()));self.assertEqual(qa['excluded_frequency_trips'],1)
if __name__=='__main__':unittest.main()
