import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-100,0),(-99,-4)).segment((-9,0)).segment((-9,-3)).segment((91,-3)).segment((91,-4)).segment((100,0)).segment((91,4)).segment((9,3)).segment((9,0)).close().assemble().finalize().extrude(-3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__141323_f85efdd4_0000.step')
