import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().arc((-2,-100),(2,0),(1,95)).segment((-2,95)).segment((-2,80)).arc((0,74),(-2,67)).close().assemble().finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00646893.step')
