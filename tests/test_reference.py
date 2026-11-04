import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_reference import validate_geometry, check

class ReferenceTests(unittest.TestCase):
    def test_committed_data(self):
        self.assertGreater(check()['metro_features'],100)
    def test_invalid_geometry(self):
        for coordinates in ([[48.8,2.3],[48.9,2.4]], [[2.3,48.8]], [[2.3,48.8],[2.3,48.8]], [[float('nan'),48.8],[2.4,48.9]]):
            with self.subTest(coordinates=coordinates), self.assertRaises(ValueError):
                validate_geometry({'type':'LineString','coordinates':coordinates})
    def test_multiline(self):
        validate_geometry({'type':'MultiLineString','coordinates':[[[2.3,48.8],[2.4,48.9]]]})
if __name__=='__main__':unittest.main()

