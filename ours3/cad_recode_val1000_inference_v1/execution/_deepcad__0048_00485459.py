import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().arc((-4,-4),(0,6),(4,-4)).segment((4,0)).segment((-4,0)).close().assemble().finalize().extrude(200).union(w0.workplane(offset=200/2).cylinder(200,5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00485459.step')
