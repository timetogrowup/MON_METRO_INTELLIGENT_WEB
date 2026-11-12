"""Exercise new modes through official classification, GTFS and dated packages."""
import csv,datetime as dt,io,pathlib,sys,unittest,zipfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from build_mobility import build,classify
import test_mobility

MODES=[('tram',None,None,'tram','0'),('rail','suburbanRailway','Transilien','train','2'),
       ('rail','regionalRail','TER','ter','2'),('rail','railShuttle',None,'shuttle','0'),
       ('cableway',None,None,'cable','6'),('funicular',None,None,'funicular','7')]
class TransportModes(unittest.TestCase):
 def reference(self):
  return test_mobility.Mobility().reference()+[dict(id_line='C9000'+str(i),name_line='Same name',transportmode=mode,transportsubmode=sub,networkname=network,operatorname='Fixture',status='active') for i,(mode,sub,network,_,_) in enumerate(MODES)]
 def archive(self,wrong_type=False,frequency=False):
  memory=io.BytesIO()
  with test_mobility.Mobility().archive() as original,zipfile.ZipFile(memory,'w') as out:
   for name in original.namelist():
    rows=list(csv.DictReader(io.StringIO(original.read(name).decode())));fields=list(rows[0])
    if name in ('routes.txt','trips.txt','stop_times.txt'):
     template=rows[:1] if name!='stop_times.txt' else rows[:4]
     if name=='trips.txt':
      fields.append('direction_id')
      for r in rows:r['direction_id']='0'
     for i,(_,_,_,_,gtfs_type) in enumerate(MODES):
      for r in template:
       r=dict(r);identifier='C9000'+str(i)
       if 'route_id' in r:r['route_id']='IDFM:'+identifier
       if 'trip_id' in r:r['trip_id']=identifier
       if name=='routes.txt':r['route_type']='3' if wrong_type else gtfs_type
       if name=='trips.txt':r['direction_id']=str(i%2)
       rows.append(r)
    text=io.StringIO();w=csv.DictWriter(text,fieldnames=fields);w.writeheader();w.writerows(rows);out.writestr(name,text.getvalue())
   if frequency:out.writestr('frequencies.txt','trip_id,start_time,end_time,headway_secs\nC90005,12:00:00,13:00:00,600\n')
  memory.seek(0);return zipfile.ZipFile(memory)
 def test_official_classification_and_exclusions(self):
  rows=self.reference();rows += [dict(rows[-1],id_line='C99999',status='prochainement active'),dict(rows[-1],id_line='C99998',transportmode='unknown')]
  selected=classify(rows,True)
  for i,(_,_,_,mode,_) in enumerate(MODES):self.assertEqual(selected['IDFM:C9000'+str(i)]['mode'],mode)
  self.assertNotIn('IDFM:C99999',selected);self.assertNotIn('IDFM:C99998',selected)
 def test_dated_departures_and_source_directions_for_every_mode(self):
  with self.archive() as z:index,packages,_=build(z,self.reference(),dt.date(2026,11,3),True)
  for i,(_,_,_,mode,_) in enumerate(MODES):
   line='IDFM:C9000'+str(i);p=packages[line]
   self.assertTrue(p['groups']);self.assertEqual(set(p['tripDirections'].values()),{str(i%2)})
 def test_gtfs_mode_mismatch_is_rejected(self):
  with self.archive(wrong_type=True) as z:
   with self.assertRaisesRegex(ValueError,'GTFS mode'):build(z,self.reference(),dt.date(2026,11,3),True)
 def test_frequency_funicular_has_no_invented_countdown(self):
  with self.archive(frequency=True) as z:_,packages,_=build(z,self.reference(),dt.date(2026,11,3),True)
  self.assertFalse(packages['IDFM:C90005']['groups'])
