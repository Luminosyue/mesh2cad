import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().arc((-100,4),(-98,3),(-95,1)).segment((-95,-2)).segment((-84,-2)).arc((-73,-2),(-62,-2)).segment((-50,5)).close().assemble().reset().face(w0.sketch().segment((-36,5),(44,-2)).segment((95,-2)).segment((95,0)).segment((98,-2)).segment((100,2)).segment((-36,5)).close().assemble()).finalize().extrude(7)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00890304.step')
