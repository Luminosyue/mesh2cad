import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-28))
r=w0.sketch().segment((-81,-94),(1,-94)).segment((1,-67)).arc((49,-19),(1,30)).segment((1,94)).segment((-81,94)).close().assemble().push([(-30,-19)]).circle(27,mode='s').finalize().extrude(1).union(w0.sketch().segment((-81,-100),(81,-100)).segment((81,100)).segment((-81,100)).segment((-81,-28)).segment((-27,-28)).segment((-27,-34)).segment((-81,-34)).close().assemble().push([(58,31)]).circle(19,mode='s').reset().face(w0.sketch().segment((42,-97),(44,-99)).segment((46,-97)).segment((44,-95)).close().assemble(),mode='s').finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0007_00076324.step')
