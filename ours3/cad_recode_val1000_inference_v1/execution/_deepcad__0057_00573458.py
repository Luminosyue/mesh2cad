import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().segment((-52,-100),(52,-100)).segment((52,42)).segment((16,14)).arc((10,1),(0,-9)).segment((0,-10)).segment((-1,-10)).arc((-17,-20),(-33,-25)).segment((-46,-34)).segment((-52,-26)).close().assemble().reset().face(w0.sketch().segment((-52,32),(-16,60)).arc((-10,73),(0,82)).segment((0,83)).segment((1,83)).arc((17,84),(33,79)).segment((46,88)).segment((52,80)).segment((52,100)).segment((-52,100)).close().assemble()).reset().face(w0.sketch().segment((-52,-98),(-25,-98)).segment((-52,-79)).close().assemble()).reset().face(w0.sketch().segment((-52,-7),(52,19)).segment((52,42)).segment((-52,10)).close().assemble()).finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0057_00573458.step')
