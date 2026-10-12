import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().segment((-5,-97),(4,-100)).segment((5,-96)).segment((5,100)).segment((-5,100)).close().assemble().finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00747343.step')
