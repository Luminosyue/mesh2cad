import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-95,0))
w1=cq.Workplane('YZ',origin=(55,0,0))
r=w0.sketch().segment((-100,-70),(-59,-70)).segment((-59,-95)).segment((100,-95)).segment((100,95)).segment((-100,95)).close().assemble().push([(-20,0)]).circle(12,mode='s').push([(16,-19)]).circle(38,mode='s').finalize().extrude(40).union(w1.sketch().segment((-95,-100),(95,-100)).segment((95,92)).segment((64,92)).segment((64,100)).segment((-64,100)).segment((-64,92)).segment((-95,92)).close().assemble().push([(0,-4)]).circle(59,mode='s').finalize().extrude(40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00799016.step')
