import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-91,0))
r=w0.sketch().segment((-100,-100),(-47,-100)).segment((-100,-61)).close().assemble().reset().face(w0.sketch().segment((-100,-48),(-10,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-16,-100),(100,-100)).segment((100,100)).segment((39,100)).close().assemble()).finalize().extrude(200).union(w1.sketch().arc((-50,-3),(-48,-10),(-47,-16)).arc((50,10),(-50,-3)).assemble().push([(0,1)]).circle(49,mode='s').finalize().extrude(172))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00980294.step')
