import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-6,-100),(6,-100)).segment((6,43)).segment((-6,43)).segment((-6,-34)).segment((-5,-34)).segment((-5,-36)).segment((-6,-36)).close().assemble().reset().face(w0.sketch().segment((-6,57),(6,57)).segment((6,100)).segment((-2,100)).arc((-3,96),(-6,96)).close().assemble()).finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00120790.step')
