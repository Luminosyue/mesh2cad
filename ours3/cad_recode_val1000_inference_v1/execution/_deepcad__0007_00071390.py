import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(33,0,0))
w1=cq.Workplane('XY',origin=(0,0,-44))
r=w0.sketch().segment((-34,-34),(79,-34)).segment((79,-29)).segment((81,-31)).segment((100,-2)).segment((100,25)).segment((56,64)).segment((52,60)).segment((7,31)).segment((10,26)).segment((-34,-10)).close().assemble().reset().face(w0.sketch().segment((10,31),(11,30)).segment((11,31)).close().assemble(),mode='s').reset().face(w0.sketch().segment((11,33),(12,33)).segment((12,34)).close().assemble(),mode='s').push([(55,44)]).circle(2,mode='s').finalize().extrude(-95).union(w0.sketch().segment((-34,-17),(-33,-17)).segment((-33,-18)).arc((-27,-2),(-34,-17)).assemble().finalize().extrude(-70)).union(w0.workplane(offset=-54/2).moveTo(46,58).cylinder(54,5)).union(w1.sketch().segment((-14,-97),(17,-97)).segment((17,-100)).segment((62,-100)).segment((62,23)).segment((46,23)).segment((46,33)).segment((-14,33)).close().assemble().push([(24,-34)]).circle(8,mode='s').finalize().extrude(-19))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0007_00071390.step')
