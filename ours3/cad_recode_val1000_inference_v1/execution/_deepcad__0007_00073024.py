import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,56,0))
r=w0.sketch().segment((-100,-73),(100,-73)).segment((100,73)).segment((-100,73)).segment((-100,-17)).segment((-98,-17)).segment((-98,-19)).segment((-100,-19)).close().assemble().push([(28,1)]).circle(41,mode='s').finalize().extrude(-112).union(w0.sketch().segment((-97,-63),(-57,-63)).segment((-57,-72)).segment((97,-72)).segment((97,72)).segment((-57,72)).segment((-57,-44)).segment((-97,-44)).close().assemble().finalize().extrude(-11))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0007_00073024.step')
