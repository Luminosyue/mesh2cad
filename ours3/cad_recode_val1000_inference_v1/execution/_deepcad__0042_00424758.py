import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,35,0))
r=w0.sketch().segment((-59,-100),(59,-100)).segment((59,-28)).segment((4,-68)).segment((-59,1)).close().assemble().reset().face(w0.sketch().segment((-59,25),(-4,68)).segment((59,1)).segment((59,100)).segment((-59,100)).close().assemble()).reset().face(w0.sketch().segment((-59,-56),(-22,-56)).segment((-59,-1)).close().assemble()).finalize().extrude(-70).union(w0.sketch().segment((-52,-23),(-46,-23)).segment((-46,-62)).segment((11,-62)).segment((11,-43)).arc((23,-40),(34,-35)).segment((52,-35)).segment((52,4)).segment((46,4)).arc((37,20),(20,30)).segment((20,35)).segment((11,35)).segment((11,74)).segment((-46,74)).segment((-46,35)).segment((-52,35)).close().assemble().push([(0,-14)]).circle(13,mode='s').finalize().extrude(-53))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00424758.step')
