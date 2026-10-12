import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,9,0))
r=w0.sketch().segment((-100,-73),(-73,-73)).segment((-73,-100)).segment((-37,-100)).segment((-73,-58)).segment((-73,-54)).segment((-10,-96)).segment((10,-73)).segment((11,-73)).segment((11,-94)).segment((45,-100)).segment((73,-100)).segment((73,-73)).segment((100,-73)).segment((100,73)).segment((73,73)).segment((73,100)).segment((57,100)).arc((30,57),(38,100)).segment((-73,100)).segment((-73,73)).segment((-100,73)).close().assemble().reset().face(w0.sketch().segment((-60,-24),(11,-65)).segment((11,-54)).segment((-47,-15)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-11,-65),(47,-15)).segment((60,24)).segment((-11,65)).close().assemble(),mode='s').finalize().extrude(-18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00656254.step')
