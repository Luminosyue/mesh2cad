import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,11,0))
r=w0.sketch().arc((-22,-80),(-1,-99),(22,-88)).segment((22,58)).segment((20,56)).arc((14,66),(5,73)).segment((22,91)).segment((20,96)).segment((0,82)).arc((-10,83),(-22,80)).segment((-22,1)).segment((-20,3)).arc((0,-7),(20,3)).segment((22,2)).segment((22,35)).segment((22,36)).segment((22,58)).segment((9,48)).segment((-22,72)).segment((-22,-74)).segment((-20,-72)).arc((-1,-82),(20,-74)).segment((22,-74)).segment((22,-73)).arc((1,-82),(-20,-74)).segment((-22,-74)).segment((-22,-75)).close().assemble().reset().face(w0.sketch().segment((-15,100),(11,97)).arc((0,100),(-15,100)).assemble()).finalize().extrude(-22)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00818044.step')
