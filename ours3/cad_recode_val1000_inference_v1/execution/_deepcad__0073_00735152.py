import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-57,0))
r=w0.sketch().segment((-57,-99),(-42,-99)).segment((-42,-100)).segment((49,-100)).segment((49,-99)).segment((57,-99)).segment((57,-71)).segment((-29,-72)).segment((-29,66)).segment((-57,66)).close().assemble().reset().face(w0.sketch().segment((-57,71),(57,72)).segment((57,99)).segment((42,99)).segment((42,100)).segment((-49,100)).segment((-49,99)).segment((-57,99)).close().assemble()).finalize().extrude(114).union(w0.sketch().segment((-57,-99),(-29,-99)).segment((-29,-71)).arc((-44,-73),(-57,-71)).close().assemble().reset().face(w0.sketch().arc((-57,71),(-44,73),(-29,71)).segment((-29,99)).segment((-57,99)).close().assemble()).finalize().extrude(114))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00735152.step')
