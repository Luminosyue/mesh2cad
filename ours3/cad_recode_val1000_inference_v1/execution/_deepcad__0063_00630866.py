import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-38))
w1=cq.Workplane('XY',origin=(0,0,-18))
r=w0.sketch().segment((-95,-30),(-93,-30)).arc((-77,-61),(-48,-84)).arc((13,-97),(66,-73)).segment((11,-39)).arc((-25,-32),(-39,5)).segment((-40,6)).segment((-39,7)).arc((-37,17),(-34,27)).segment((-33,28)).segment((-34,29)).arc((-61,57),(-93,37)).segment((-94,37)).segment((-94,36)).arc((-99,3),(-95,-29)).close().assemble().reset().face(w0.sketch().segment((-83,52),(-48,86)).arc((-68,70),(-83,52)).assemble()).reset().face(w0.sketch().segment((-35,93),(27,30)).arc((54,38),(70,18)).segment((95,3)).arc((54,82),(-35,93)).assemble()).finalize().extrude(76).union(w1.sketch().arc((94,-31),(99,0),(94,31)).close().assemble().finalize().extrude(51))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0063_00630866.step')
