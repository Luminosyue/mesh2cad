import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-18,0))
r=w0.sketch().segment((-100,-19),(100,-19)).segment((100,19)).segment((-100,19)).segment((-100,12)).segment((-98,12)).segment((-98,10)).segment((-100,10)).close().assemble().finalize().extrude(36).union(w0.sketch().segment((-87,-19),(87,-19)).segment((87,19)).segment((-35,19)).arc((-57,-8),(-87,-19)).assemble().finalize().extrude(36))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00874573.step')
