import unittest,ast,tempfile,pathlib
from fusion_unit_contract import transform
class Tests(unittest.TestCase):
 def test_dims_and_directions(self):
  src='a = Box(width=2, depth=3, height=4, origin=(1,2,3), axis=(0,1,0), x_axis=(1,0,0))'
  kw={k.arg:ast.literal_eval(k.value) for k in ast.parse(transform(src,10)).body[0].value.keywords}
  self.assertEqual(kw,dict(width=20,depth=30,height=40,origin=(10,20,30),axis=(0,1,0),x_axis=(1,0,0)))
 def test_nested_boolean_polygon(self):
  src='a=Extrude(Circle(radius=2),height=3,axis=(0,0,1),origin=(0,0,0))\nb=ExtrudePolygon(points=[(0,0),(1,0),(0,1)],height=1,height_two=2,symmetric=True,axis=(0,0,1),origin=(1,2,3),x_axis=(1,0,0))\nc=Cut(a,b)\nresult=c'
  got=transform(src,10,(1,2,3));self.assertIn('radius=20',got);self.assertIn('height_two=20',got);self.assertIn('symmetric=True',got);self.assertIn('Cut(a, b)',got);self.assertIn('origin=(11, 22, 33)',got)
 def test_extent_kwargs_and_negative_height(self):
  src='a=Extrude(Circle(radius=2),height=-3,axis=(0,0,1),origin=(0,0,0),symmetric=True)\nb=Box(width=1,depth=2,height=4,height_two=-0.5,origin=(1,2,3),axis=(0,1,0),x_axis=(1,0,0))\nresult=b'
  got=transform(src,10,(1,2,3))
  self.assertIn('radius=20',got);self.assertIn('height=-30',got);self.assertIn('symmetric=True',got)
  self.assertIn('height_two=-5',got);self.assertIn('origin=(11, 22, 33)',got)
 def test_reject_unknown(self):
  for s in ['a=Loft(height=2)','a=Circle(radius=1,angle=3)','a=Box(width=1,depth=1,height=1)','a=Extrude(2,height=3,origin=(0,0,0))']:
   with self.assertRaises(ValueError):transform(s,10)
 def test_geometry_area_volume(self):
  import cadquery as cq
  from edge_aware_cad_planner_v1.cad_dsl import execute_dsl
  src='a=Box(width=2,depth=3,height=4,origin=(1,2,3),axis=(0,0,1),x_axis=(1,0,0))'
  with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as d:
   shapes=[]
   for i,s in enumerate([src,transform(src,10)]):
    p=pathlib.Path(d)/f'{i}.step';execute_dsl(s,p);shapes.append(cq.importers.importStep(str(p)).val())
   self.assertAlmostEqual(shapes[1].Area()/shapes[0].Area(),100,places=6);self.assertAlmostEqual(shapes[1].Volume()/shapes[0].Volume(),1000,places=6)
if __name__=='__main__':unittest.main()
