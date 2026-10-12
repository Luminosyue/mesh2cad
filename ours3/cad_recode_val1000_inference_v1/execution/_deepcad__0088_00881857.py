import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().segment((-100,-15),(-35,-15)).segment((-35,-14)).segment((100,-14)).segment((100,14)).segment((-100,15)).close().assemble().finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00881857.step')
