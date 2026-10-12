import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().segment((-4,-97),(3,-100)).segment((4,-96)).segment((4,96)).segment((-4,100)).close().assemble().finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00226959.step')
