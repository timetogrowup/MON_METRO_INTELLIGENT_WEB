import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from match_shapes import align
class Matching(unittest.TestCase):
    def test_monotonic_projection(self):
        line=[[2.3,48.8],[2.31,48.8],[2.32,48.8]]
        result=align([[2.305,48.8001],[2.315,48.8001]],line)
        self.assertAlmostEqual(result[0][2],0.5,places=4)
        self.assertLess(result[0][2],result[1][2])
    def test_far_and_reversed(self):
        line=[[2.3,48.8],[2.31,48.8],[2.32,48.8]]
        for points in ([[2.3,49.0],[2.31,49.0]],[[2.319,48.8],[2.301,48.8]]):
            with self.assertRaises(ValueError):align(points,line)
if __name__=='__main__':unittest.main()

