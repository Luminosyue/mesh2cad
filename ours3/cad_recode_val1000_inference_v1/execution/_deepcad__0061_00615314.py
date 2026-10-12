import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('YZ',origin=(-28,0,0))
r=w0.sketch().segment((-66,-79),(66,-79)).segment((66,63)).arc((49,32),(17,12)).segment((17,-1)).segment((-17,-1)).segment((-17,12)).arc((-49,32),(-66,63)).close().assemble().reset().face(w0.sketch().arc((-66,68),(-36,81),(-5,75)).segment((-5,82)).segment((-66,82)).close().assemble()).finalize().extrude(44).union(w1.sketch().segment((-92,-66),(48,-66)).segment((48,-55)).arc((72,-58),(92,-47)).segment((100,-47)).segment((100,62)).segment((92,62)).arc((72,73),(48,75)).segment((48,66)).segment((-92,66)).close().assemble().reset().face(w1.sketch().arc((-56,-38),(12,-61),(6,-1)).arc((1,1),(-2,6)).arc((-28,10),(-50,-4)).arc((-52,-11),(-54,-18)).segment((-56,-18)).close().assemble(),mode='s').push([(54,60)]).circle(7,mode='s').finalize().extrude(-54))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00615314.step')
