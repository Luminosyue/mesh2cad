import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-4,-100),(4,-100)).segment((4,-68)).segment((-4,-61)).close().assemble().reset().face(w0.sketch().segment((-4,-15),(4,-22)).segment((4,100)).segment((-4,100)).close().assemble()).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0004_00042173.step')
