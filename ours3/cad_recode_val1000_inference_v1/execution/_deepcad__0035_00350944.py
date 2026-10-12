import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-25,0))
r=w0.sketch().segment((-100,-50),(100,-50)).segment((100,50)).segment((44,50)).segment((92,-13)).segment((46,-44)).segment((46,-50)).segment((37,-50)).segment((-10,-50)).segment((-10,-49)).segment((-46,-49)).segment((-46,-50)).segment((-100,-50)).close().assemble().reset().face(w0.sketch().segment((-100,-4),(-10,42)).segment((-10,50)).segment((-100,50)).close().assemble()).finalize().extrude(50)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00350944.step')
