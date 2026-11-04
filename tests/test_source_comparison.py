import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compare_sources import distance_to_edge
class SourceComparison(unittest.TestCase):
    def test_projection_and_endpoints(self):
        self.assertLess(distance_to_edge((2.305,48.8),(2.3,48.8),(2.31,48.8)),.01)
        self.assertAlmostEqual(distance_to_edge((2.305,48.801),(2.3,48.8),(2.31,48.8)),111.32,places=2)
        self.assertGreater(distance_to_edge((2.32,48.8),(2.3,48.8),(2.31,48.8)),700)
    def test_degenerate(self):self.assertEqual(distance_to_edge((2.3,48.8),(2.3,48.8),(2.3,48.8)),0)
if __name__=='__main__':unittest.main()

