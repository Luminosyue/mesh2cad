import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14637, 0.28976, 0.35417), normal=(-0.43464, -0.9006, -0.0), xDir=(-0.9006, 0.43464, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15912, -0.20261)
loop_1 = loop_1.lineTo(0.15912, -0.45583)
loop_1 = loop_1.lineTo(0.13848, -0.45583)
loop_1 = loop_1.lineTo(0.14229, -0.43466)
loop_1 = loop_1.lineTo(0.14605, -0.41163)
loop_1 = loop_1.lineTo(0.13928, -0.38682)
loop_1 = loop_1.lineTo(0.12631, -0.37294)
loop_1 = loop_1.lineTo(0.10977, -0.35972)
loop_1 = loop_1.lineTo(0.09358, -0.3376)
loop_1 = loop_1.lineTo(0.11192, -0.31349)
loop_1 = loop_1.lineTo(0.1158, -0.30058)
loop_1 = loop_1.threePointArc((0.12761, -0.28142), (0.13891, -0.26358))
loop_1 = loop_1.threePointArc((0.14724, -0.24312), (0.15386, -0.22653))
loop_1 = loop_1.lineTo(0.15853, -0.20475)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_37_interval_0.stl')