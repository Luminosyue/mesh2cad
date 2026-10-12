import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-80,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,-20)).segment((-23,-20)).segment((-23,10)).arc((-24,11),(-24,12)).segment((-23,12)).segment((-23,71)).segment((-24,71)).arc((-24,72),(-23,73)).segment((-23,100)).segment((-100,100)).close().assemble().finalize().extrude(160).union(w0.sketch().segment((-97,-97),(-60,-97)).arc((-69,-74),(-60,-51)).segment((-97,-51)).close().assemble().reset().face(w0.sketch().arc((-57,-51),(-56,-52),(-55,-52)).arc((-55,-51),(-54,-51)).arc((-54,-49),(-55,-48)).arc((-56,-50),(-57,-51)).assemble()).reset().face(w0.sketch().segment((-37,-20),(78,-20)).arc((21,-1),(-37,-20)).assemble()).reset().face(w0.sketch().arc((49,-97),(68,-54),(68,-10)).segment((49,-10)).close().assemble()).finalize().extrude(160))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00741928.step')
