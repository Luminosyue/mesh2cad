import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('YZ',origin=(-44,0,0))
r=w0.sketch().segment((-66,-15),(-34,-15)).segment((-34,-44)).segment((34,-44)).segment((34,-15)).segment((66,-15)).segment((66,14)).segment((34,14)).segment((34,44)).segment((-34,44)).segment((-34,14)).segment((-66,14)).close().assemble().finalize().extrude(44).union(w0.sketch().segment((-71,-37),(-42,-37)).arc((-61,0),(-42,37)).segment((-71,37)).close().assemble().reset().face(w0.sketch().segment((-16,-10),(16,-10)).segment((16,10)).segment((-16,10)).arc((-10,0),(-16,-10)).assemble()).finalize().extrude(182)).union(w1.sketch().arc((-79,-71),(0,-51),(85,-71)).segment((100,-71)).segment((100,71)).segment((-79,71)).close().assemble().push([(66,1)]).circle(17,mode='s').finalize().extrude(89))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00148247.step')
