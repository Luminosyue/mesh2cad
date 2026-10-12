import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.87834, 0.23909, 0.04286), normal=(-0.07957, -0.9967, 0.01616), xDir=(-0.99683, 0.07958, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12793, -0.06068)
loop_1 = loop_1.lineTo(-0.08664, -0.06069)
loop_1 = loop_1.lineTo(-0.06046, -0.0822)
loop_1 = loop_1.threePointArc((-0.04874, -0.08244), (-0.03749, -0.08257))
loop_1 = loop_1.lineTo(-0.01363, -0.08164)
loop_1 = loop_1.lineTo(-0.00161, -0.08092)
loop_1 = loop_1.lineTo(0.01553, -0.08008)
loop_1 = loop_1.lineTo(0.0312, -0.07814)
loop_1 = loop_1.lineTo(0.12793, -0.06068)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_3_interval_0.stl')