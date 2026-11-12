import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from build_mobility import classify
from test_mobility import Mobility
class LineColours(unittest.TestCase):
 def test_official_fields_are_kept_by_line_id(self):
  rows=Mobility().reference()
  rows[-1].update(colourweb_hexa='0055c8',textcolourweb_hexa='ffffff')
  rows.append(dict(rows[-1],id_line='C99999',colourweb_hexa='ffbe00',textcolourweb_hexa='000000'))
  lines=classify(rows,True)
  self.assertEqual(lines['IDFM:C01122']['route_color'],'0055C8')
  self.assertEqual(lines['IDFM:C99999']['route_color'],'FFBE00')
  self.assertEqual(lines['IDFM:C99999']['route_text_color'],'000000')
 def test_invalid_and_missing_colours_keep_an_empty_fallback(self):
  rows=Mobility().reference();rows[-1]['colourweb_hexa']='red;background:url(x)'
  line=classify(rows,True)['IDFM:C01122']
  self.assertEqual(line['route_color'],'');self.assertEqual(line['route_text_color'],'')
