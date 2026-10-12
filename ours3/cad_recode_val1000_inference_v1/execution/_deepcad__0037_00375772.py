import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-84,0),(-83,0)).segment((-83,-46)).segment((-69,-46)).arc((-76,-2),(-60,42)).segment((-83,42)).segment((-83,4)).segment((-84,4)).close().assemble().reset().face(w0.sketch().segment((-44,-67),(-17,-67)).segment((-17,0)).segment((84,0)).segment((84,4)).segment((83,4)).segment((83,67)).segment((-44,67)).segment((-44,42)).segment((-17,42)).segment((-17,4)).segment((-44,4)).close().assemble()).finalize().extrude(200).union(w0.sketch().segment((-83,-67),(-17,-67)).segment((-17,0)).segment((75,0)).segment((75,67)).segment((-83,67)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0037_00375772.step')
