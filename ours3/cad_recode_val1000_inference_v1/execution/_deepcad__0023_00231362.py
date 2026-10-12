import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-18,0))
r=w0.sketch().segment((-100,-17),(-95,-17)).segment((-95,-13)).segment((-92,-13)).segment((-92,-17)).segment((100,-17)).segment((100,17)).segment((-100,18)).close().assemble().reset().face(w0.sketch().segment((-5,15),(-4,14)).segment((-4,15)).segment((-5,16)).close().assemble(),mode='s').finalize().extrude(36)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0023_00231362.step')
