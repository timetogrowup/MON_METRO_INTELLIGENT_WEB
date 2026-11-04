import csv,datetime as dt,io,json,pathlib,sys,tempfile,unittest,zipfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from build_mobility import build,classify,RER,BUS,SCOPE

class Mobility(unittest.TestCase):
 def reference(self):return [{'id_line':k,'name_line':(RER|BUS)[k],'transportmode':'rail' if v=='rer' else 'bus','transportsubmode':'local','networkname':'RER' if v=='rer' else 'bus','operatorname':'Fixture','status':'active'} for k,v in SCOPE.items()]
 def archive(self,frequency=False):
  memory=io.BytesIO()
  with zipfile.ZipFile(memory,'w') as z:
   def put(name,rows):
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);z.writestr(name+'.txt',s.getvalue())
   put('agency',[{'agency_id':'x','agency_timezone':'Europe/Paris'}]);put('routes',[{'route_id':'IDFM:'+k,'route_type':'2' if v=='rer' else '3','agency_id':'x'} for k,v in SCOPE.items()]);put('calendar_dates',[{'service_id':'s','date':'20261103','exception_type':'1'}]);put('trips',[{'trip_id':k,'route_id':'IDFM:'+k,'service_id':'s'} for k in SCOPE]);put('stops',[{'stop_id':s,'parent_station':'','stop_name':s,'stop_lat':'48.85','stop_lon':'2.35'} for s in ['a','b','c']]);rows=[]
   for k in SCOPE:
    for i,(stop,time,pickup) in enumerate([('a','12:00:00','0'),('b','12:02:00','3'),('a','12:04:00','0'),('c','12:06:00','0')],1):rows.append({'trip_id':k,'stop_id':stop,'stop_sequence':str(i),'departure_time':time,'pickup_type':pickup})
   put('stop_times',rows)
   if frequency:put('frequencies',[{'trip_id':next(iter(SCOPE)),'start_time':'12:00:00','end_time':'13:00:00','headway_secs':'600'}])
  memory.seek(0);return zipfile.ZipFile(memory)
 def test_classification_is_not_based_on_letter_or_gtfs_rail_code(self):
  r=self.reference();r[0]['networkname']='Transilien'
  with self.assertRaises(ValueError):classify(r)
  self.assertEqual(set(classify(self.reference())),{'IDFM:'+k for k in SCOPE})
 def test_loops_separate_visits_and_conditional_boarding_omitted(self):
  with self.archive() as z:d,packages,qa=build(z,self.reference(),dt.date(2026,11,3))
  self.assertEqual(len(d['lines']),10)
  for line,p in packages.items():
   self.assertEqual(len(p['groups']),1);key,rows=next(iter(p['groups'].items()));self.assertEqual(json.loads(key),['a',line,'c']);self.assertEqual([r[3] for r in rows],[1,3])
  self.assertGreater(qa['excluded_conditional_boarding_rows'],0)
 def test_frequency_only_line_cannot_be_published_as_exact_departures(self):
  with self.archive(True) as z:
   with self.assertRaises(ValueError):build(z,self.reference(),dt.date(2026,11,3))

if __name__=='__main__':unittest.main()

