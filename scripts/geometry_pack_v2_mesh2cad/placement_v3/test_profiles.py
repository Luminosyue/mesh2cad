import unittest,numpy as np
from fusion360_to_dsl import _sample_loop,_sample_nurbs,_sample_arc,Fusion360FilterError
from test_placement import lines
class Profiles(unittest.TestCase):
 def test_unordered_reversed_edges(self):
  c=lines([(0,0),(2,0),(2,1),(0,1)]);c=[c[0],c[2],c[3],c[1]];c[1]['start_point'],c[1]['end_point']=c[1]['end_point'],c[1]['start_point']
  p=np.array(_sample_loop(c));np.testing.assert_allclose(p,[(0,0),(2,0),(2,1),(0,1)])
 def test_open_loop_rejected(self):
  with self.assertRaises(Fusion360FilterError):_sample_loop(lines([(0,0),(2,0),(2,1),(0,1)])[:-1])
 def test_rational_quarter_circle(self):
  c={'degree':2,'knots':[0,0,0,1,1,1],'weights':[1,2**-.5,1],'control_points':[dict(x=x,y=y) for x,y in [(1,0),(1,1),(0,1)]]}
  p=np.array(_sample_nurbs(c));np.testing.assert_allclose(np.linalg.norm(p,axis=1),1,atol=1e-12);self.assertTrue(np.all(p>=0))
 def test_arc_negative_normal(self):
  c={'center_point':dict(x=0,y=0),'radius':2,'start_angle':0,'end_angle':np.pi/2,'normal':dict(x=0,y=0,z=-1)}
  p=_sample_arc(c);np.testing.assert_allclose(p[0],[2,0],atol=1e-12);np.testing.assert_allclose(p[-1],[0,-2],atol=1e-12)
if __name__=='__main__':unittest.main()
