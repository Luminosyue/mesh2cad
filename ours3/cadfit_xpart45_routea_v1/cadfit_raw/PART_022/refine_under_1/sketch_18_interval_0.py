import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02464, -0.95184, 0.0965), normal=(-7e-05, 0.99999, -0.00529), xDir=(1.0, 7e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14811, 0.3213)
loop_1 = loop_1.lineTo(0.25631, 0.30941)
loop_1 = loop_1.lineTo(0.26641, 0.30486)
loop_1 = loop_1.lineTo(0.27102, 0.18892)
loop_1 = loop_1.lineTo(-0.18928, 0.20246)
loop_1 = loop_1.lineTo(-0.18381, 0.31112)
loop_1 = loop_1.lineTo(-0.17059, 0.31563)
loop_1 = loop_1.lineTo(-0.14899, 0.32083)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.86)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_18_interval_0.stl')