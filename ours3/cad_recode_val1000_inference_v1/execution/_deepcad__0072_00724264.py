import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,39,0))
w1=cq.Workplane('YZ',origin=(41,0,0))
r=w0.sketch().segment((-46,74),(-24,74)).segment((-24,45)).segment((-25,45)).segment((-25,34)).segment((-26,34)).segment((-26,-59)).segment((-1,-59)).segment((-1,-5)).segment((0,-5)).segment((1,35)).segment((-1,35)).segment((-1,45)).segment((-24,45)).segment((-24,74)).segment((-1,74)).segment((-1,75)).segment((2,75)).segment((2,99)).segment((-46,100)).close().assemble().reset().face(w0.sketch().segment((-28,-100),(40,-100)).segment((40,-91)).segment((46,-91)).segment((46,-76)).segment((24,-75)).segment((24,-76)).segment((26,-76)).segment((26,-77)).segment((24,-77)).segment((24,-78)).segment((23,-78)).segment((23,-77)).segment((20,-77)).segment((20,-76)).segment((23,-76)).segment((23,-75)).segment((-27,-75)).segment((-27,-57)).segment((-28,-57)).close().assemble()).finalize().extrude(-78).union(w0.sketch().arc((-25,59),(-24,61),(-24,63)).segment((-25,63)).close().assemble().finalize().extrude(-37)).union(w1.workplane(offset=59/2).moveTo(11,1).cylinder(59,7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00724264.step')
