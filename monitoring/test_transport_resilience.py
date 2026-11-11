import datetime as dt
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
from check_transport_health import check, verified
from validate_transport_reserve import coverage

UTC=dt.timezone.utc
class ResilienceTest(unittest.TestCase):
    def test_integrity_failure_rejected(self):
        with patch('check_transport_health.fetch_json',return_value=({},b'bad')):
            with self.assertRaises(ValueError):verified('line.json',dict(bytes=3,sha256='0'*64))
    def test_stale_deployment_rejected(self):
        now=dt.datetime(2026,11,11,12,tzinfo=UTC)
        live=dict(validFromUtc='2026-11-11T00:00:00+00:00',validUntilUtc='2026-11-15T00:00:00+00:00')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'timetable').mkdir();(root/'timetable'/'manifest.json').write_text(json.dumps({**live,'version':'new'}))
            with patch('check_transport_health.fetch_json',return_value=(live,b'')):
                self.assertEqual(check('timetable',now,expected_root=root)['state'],'stale')
    def test_network_failure_retried_once(self):
        with patch('check_transport_health.fetch_json',side_effect=OSError('offline')) as fetch,patch('check_transport_health.time.sleep'):
            self.assertEqual(check('mobility',dt.datetime.now(UTC))['state'],'unreachable');self.assertEqual(fetch.call_count,2)
    def test_four_real_days_and_dst(self):
        tz=ZoneInfo('Europe/Paris')
        for first in [dt.datetime(2026,11,11,tzinfo=tz),dt.datetime(2027,3,27,tzinfo=tz)]:
            last=first+dt.timedelta(days=4)
            manifest=dict(validFromUtc=first.astimezone(UTC).isoformat(),validUntilUtc=last.astimezone(UTC).isoformat(),lines={'a':{'file':'a.json'}})
            rows=[[int((first+dt.timedelta(days=i,hours=12)).timestamp())] for i in range(4)]
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);file=root/'a.json';file.write_text(json.dumps({'groups':{'s':rows}}));self.assertEqual(len(coverage(root,manifest)),4)
                file.write_text(json.dumps({'groups':{'s':rows[:-1]}}))
                with self.assertRaises(ValueError):coverage(root,manifest)
if __name__=='__main__':unittest.main()
