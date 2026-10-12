import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28007, -0.34499)
loop_1 = loop_1.lineTo(0.26936, -0.35135)
loop_1 = loop_1.threePointArc((0.26028, -0.35394), (0.25251, -0.356))
loop_1 = loop_1.threePointArc((0.24325, -0.35663), (0.23601, -0.35722))
loop_1 = loop_1.lineTo(0.21806, -0.35246)
loop_1 = loop_1.threePointArc((0.21254, -0.34884), (0.20718, -0.34547))
loop_1 = loop_1.lineTo(0.19205, -0.32524)
loop_1 = loop_1.threePointArc((0.18976, -0.31774), (0.18744, -0.31057))
loop_1 = loop_1.lineTo(0.19027, -0.29219)
loop_1 = loop_1.lineTo(0.19867, -0.28089)
loop_1 = loop_1.threePointArc((0.21131, -0.27289), (0.21945, -0.26947))
loop_1 = loop_1.threePointArc((0.22875, -0.26808), (0.23609, -0.26693))
loop_1 = loop_1.threePointArc((0.24508, -0.2671), (0.25272, -0.26733))
loop_1 = loop_1.threePointArc((0.26191, -0.27001), (0.2698, -0.27234))
loop_1 = loop_1.lineTo(0.28044, -0.33418)
loop_1 = loop_1.lineTo(0.28007, -0.34499)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_31_interval_0.stl')