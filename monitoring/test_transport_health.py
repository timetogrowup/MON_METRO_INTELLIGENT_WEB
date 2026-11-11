import datetime as dt
import unittest
from check_transport_health import assess

class HealthTest(unittest.TestCase):
    now = dt.datetime(2026, 11, 11, 12, tzinfo=dt.timezone.utc)
    def manifest(self, hours, start=-12):
        return dict(validFromUtc=(self.now+dt.timedelta(hours=start)).isoformat(), validUntilUtc=(self.now+dt.timedelta(hours=hours)).isoformat())
    def test_thresholds(self):
        for hours, state in [(30,'healthy'),(18,'healthy'),(17.99,'warning'),(0,'expired'),(-1,'expired')]:
            with self.subTest(hours=hours): self.assertEqual(assess(self.manifest(hours),self.now)['state'],state)
    def test_future(self):
        self.assertEqual(assess(self.manifest(30,1),self.now)['state'],'future')
    def test_invalid(self):
        for data in [{},None,dict(validFromUtc='oops',validUntilUtc='oops'),dict(validFromUtc='2026-11-11',validUntilUtc='2026-11-12'),self.manifest(-20)]:
            self.assertEqual(assess(data,self.now)['state'],'invalid')

if __name__ == '__main__': unittest.main()
