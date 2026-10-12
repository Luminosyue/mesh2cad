import unittest,math,json,pathlib
from fusion360_to_dsl import _loop_region,fusion360_json_to_dsl
def circle(r,x=0):return {'type':'Circle3D','radius':r,'center_point':{'x':x,'y':0}}
def line(a,b):return {'type':'Line3D','start_point':dict(x=a,y=0),'end_point':dict(x=b,y=0)}
class Regions(unittest.TestCase):
 def test_annulus_bridge(self):
  g,d=_loop_region([circle(2),circle(1),line(1,2)]);self.assertAlmostEqual(g.area/(3*math.pi),1,delta=.002);self.assertEqual(len(g.interiors),1)
 def test_disjoint_circles_bridge(self):
  g,d=_loop_region([circle(1),circle(1,5),line(1,4)]);self.assertAlmostEqual(g.area/(2*math.pi),1,delta=.002);self.assertEqual(len(g.geoms),2)
 def test_three_real_regression_profiles(self):
  root=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/train')
  for sid in ['33607_c6f31fa6_0010','53222_e9c623af_0002','57738_4610041b_0000']:
   with self.subTest(sid=sid):
    code,report=fusion360_json_to_dsl(json.loads((root/sid/'source.json').read_text()));self.assertTrue(any(x['profile_kind']=='complex_region' for x in report['operations']))
if __name__=='__main__':unittest.main()
