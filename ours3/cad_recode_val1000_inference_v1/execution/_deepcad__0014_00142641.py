import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-5,-96),(4,-100)).segment((5,-96)).segment((5,91)).segment((-2,100)).segment((-5,91)).close().assemble().finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00142641.step')
