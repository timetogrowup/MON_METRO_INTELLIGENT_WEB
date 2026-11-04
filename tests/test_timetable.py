import datetime as dt, io, zipfile, unittest,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from build_timetable import active_services,seconds,instant,build,next_visit
class Timetable(unittest.TestCase):
 def test_calendar_exceptions(self):
  day=dt.date(2026,11,3);c=[dict(service_id='A',start_date='20260101',end_date='20261231',tuesday='1')]
  self.assertEqual(active_services(c,[dict(service_id='A',date='20261103',exception_type='2'),dict(service_id='B',date='20261103',exception_type='1')],day),{'B'})
 def test_after_midnight_and_previous_service_day(self):
  day=dt.date(2026,11,3);self.assertEqual(instant(day,'25:10:00'),int(dt.datetime(2026,11,4,0,10,tzinfo=dt.timezone.utc).timestamp()));self.assertEqual(seconds('25:10:00'),90600)
 def test_dst_uses_noon_minus_twelve_hours(self):
  self.assertEqual(instant(dt.date(2026,10,25),'02:30:00'),int(dt.datetime(2026,10,25,1,30,tzinfo=dt.timezone.utc).timestamp()))
  self.assertEqual(instant(dt.date(2026,3,29),'02:30:00'),int(dt.datetime(2026,3,29,0,30,tzinfo=dt.timezone.utc).timestamp()))
 def test_invalid_time_rejected(self):
  for value in ['12:60:00','-1:00:00','168:00:00','12:00']:
   with self.assertRaises(ValueError):seconds(value)
 def test_real_builder_calendar_pickup_and_previous_day(self):
  content=io.BytesIO()
  with zipfile.ZipFile(content,'w') as z:
   z.writestr('agency.txt','agency_id,agency_timezone\na,Europe/Paris\n')
   z.writestr('routes.txt','route_id,agency_id\nIDFM:C01371,a\nIDFM:C01374,a\n')
   z.writestr('trips.txt','trip_id,route_id,service_id\nt1,IDFM:C01371,previous\nt4,IDFM:C01374,today\n')
   z.writestr('calendar_dates.txt','service_id,date,exception_type\nprevious,20261102,1\ntoday,20261103,1\n')
   z.writestr('stop_times.txt','trip_id,stop_sequence,stop_id,departure_time,pickup_type\nt1,1,s,25:10:00,0\nt1,2,d,25:20:00,1\nt4,1,s,12:00:00,0\nt4,2,d,12:10:00,1\n')
  network={'lines':[{'route_id':line,'route_type':'1'} for line in ['IDFM:C01371','IDFM:C01374']],'patterns':[{'route_id':line,'stop_ids':['s','d']} for line in ['IDFM:C01371','IDFM:C01374']]}
  with zipfile.ZipFile(content) as z:result,qa=build(z,network,dt.date(2026,11,3))
  self.assertEqual(qa['departures'],2);row=next(iter(result['IDFM:C01371']['groups'].values()))[0];self.assertEqual(row[1],'2026-11-02');self.assertEqual(row[0],instant(dt.date(2026,11,2),'25:10:00'))
 def test_publication_validator_rejects_stale_and_corrupt(self):
  import tempfile,json,hashlib
  from validate_timetable import check
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);target=root/'timetable';target.mkdir()
   network={'lines':[{'route_id':line,'route_type':'1'} for line in ['IDFM:C01371','IDFM:C01374']],'patterns':[{'route_id':line,'stop_ids':['s','d']} for line in ['IDFM:C01371','IDFM:C01374']]};raw=json.dumps(network).encode();(root/'network.json').write_bytes(raw)
   start='2026-11-03T00:00:00+00:00';end='2026-11-05T00:00:00+00:00';moment=dt.datetime(2026,11,3,12,tzinfo=dt.timezone.utc);files={}
   for line in ['IDFM:C01371','IDFM:C01374']:
    key=json.dumps(['s',line,'d'],separators=(',',':'));data={'schemaVersion':1,'lineId':line,'validFromUtc':start,'validUntilUtc':end,'groups':{key:[[int(moment.timestamp())+60,'2026-11-03','a'*16,1]]}}
    payload=json.dumps(data).encode();name=line.replace(':','-')+'.json';(target/name).write_bytes(payload);files[line]={'file':name,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'groups':1}
   m={'schemaVersion':1,'quality':'timetable','source':'https://eu.ftp.opendatasoft.com/stif/GTFS/IDFM-gtfs.zip','sourceSha256':'a'*64,'networkSha256':hashlib.sha256(raw).hexdigest(),'validFromUtc':start,'validUntilUtc':end,'generatedAtUtc':moment.isoformat(),'lines':files,'qa':{'departures':2,'groups':2}}
   (target/'manifest.json').write_text(json.dumps(m));self.assertEqual(check(root,moment)['departures'],2)
   with self.assertRaises(AssertionError):check(root,moment+dt.timedelta(days=3))
   (target/files['IDFM:C01371']['file']).write_bytes(b'corrupt')
   with self.assertRaises(AssertionError):check(root,moment)

 def test_metro_scope_is_reference_driven_and_excludes_other_modes(self):
  from build_timetable import metro_scope
  network={'lines':[{'route_id':'metro-3','route_type':'1'},{'route_id':'metro-14','route_type':'1'},{'route_id':'bus','route_type':'3'},{'route_id':'rail','route_type':'2'}]}
  self.assertEqual(metro_scope(network),{'metro-3','metro-14'})
  with self.assertRaises(ValueError):metro_scope({'lines':[{'route_id':'bus','route_type':'3'}]})
 def test_secret_audit_never_exports_the_secret(self):
  from audit_prim import report
  import json
  secret='fixture-value-never-export'
  result=report({'PRIM_API_KEY':secret});self.assertTrue(result['configured']);self.assertNotIn(secret,json.dumps(result));self.assertFalse(result['liveCallPerformed']);self.assertFalse(report({})['configured'])

 def test_first_departure_station_skips_same_place_and_noncommercial_points(self):
  stops={k:{'parent_station':parent} for k,parent in [('p1','P'),('p2','P'),('pass','X'),('next','N')]}
  rules=[{}, {}, {'pickup_type':'1','drop_off_type':'1'}, {}]
  self.assertEqual(next_visit(['p1','p2','pass','next'],rules,[1,2,3,4],0,stops),('next',4))
  self.assertEqual(next_visit(['p1','p2','pass','next'],rules,[1,2,3,4],1,stops),('next',4))
  self.assertIsNone(next_visit(['p1','p2'],[{},{}],[1,2],0,stops))

