import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
r=w0.sketch().arc((-3,-96),(0,-98),(-2,-100)).segment((3,-97)).segment((3,96)).arc((-3,90),(-3,82)).close().assemble().finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00173572.step')
