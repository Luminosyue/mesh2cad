import unittest,ast,pathlib,tempfile,sys,json
import numpy as np
from fusion360_to_dsl import _emit_extrude_body,_is_rect_loop,_profile_point_to_world,fusion360_json_to_dsl
from cad_dsl import execute_dsl
E={'height':2,'height_two':0,'symmetric':False}
F=((10,20,30),(1,0,0),(0,0,-1))
def lines(points):return [{'type':'Line3D','start_point':dict(x=a[0],y=a[1]),'end_point':dict(x=b[0],y=b[1])} for a,b in zip(points,points[1:]+points[:1])]
def kw(code):return {k.arg:ast.literal_eval(k.value) for k in ast.parse(code).body[0].value.keywords}
class Placement(unittest.TestCase):
 def test_circle_world_center(self):
  code,_=_emit_extrude_body('a',[{'type':'Circle3D','radius':2,'center_point':{'x':3,'y':4}}],F,E)
  self.assertEqual(kw(code)['origin'],(10,24,27));self.assertEqual(kw(code)['axis'],(1,0,0))
 def test_box_center(self):
  code,_=_emit_extrude_body('a',lines([(2,3),(6,3),(6,5),(2,5)]),F,E)
  self.assertEqual(kw(code)['origin'],(10,24,26));self.assertEqual(kw(code)['width'],4);self.assertEqual(kw(code)['depth'],2)
 def test_rotated_rectangle_not_aabb(self):
  curves=lines([(0,1),(1,2),(3,0),(2,-1)])
  self.assertFalse(_is_rect_loop(curves)[0]);code,_=_emit_extrude_body('a',curves,F,E);self.assertIn('ExtrudePolygon',code)
 def test_trapezoid_not_box(self):self.assertFalse(_is_rect_loop(lines([(0,0),(4,0),(3,2),(1,2)]))[0])
 def test_zero_center_unchanged(self):
  c,_=_emit_extrude_body('a',[{'type':'Circle3D','radius':1,'center_point':{'x':0,'y':0}}],F,E);self.assertEqual(kw(c)['origin'],F[0])
 def test_preserve_extent(self):
  for curves in [lines([(2,3),(6,3),(6,5),(2,5)]),[{'type':'Circle3D','radius':1,'center_point':{'x':2,'y':3}}]]:
   c,_=_emit_extrude_body('a',curves,F,dict(E,height=-3,height_two=4));self.assertEqual(kw(c)['height'],-3);self.assertEqual(kw(c)['height_two'],4)
 def test_true_geometry_box(self):
  import cadquery as cq
  c,_=_emit_extrude_body('a',lines([(2,3),(6,3),(6,5),(2,5)]),F,E)
  with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as d:
   p=pathlib.Path(d)/'a.step';execute_dsl(c+'\nresult=a',p);s=cq.importers.importStep(str(p)).val();b=s.BoundingBox();np.testing.assert_allclose([b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],[10,12,23,25,24,28],atol=1e-6)
 def test_real_21865_center(self):
  p=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/train/21865_c190b734_0000/source.json');c,_=fusion360_json_to_dsl(json.loads(p.read_text()));k=kw(c.splitlines()[1]);np.testing.assert_allclose(k['origin'],[0,1.648939,43.219624],atol=1e-6);self.assertTrue(k['symmetric'])
if __name__=='__main__':unittest.main()
