import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.15466, 0.19883, -0.04858), normal=(-0.00109, -1.0, 0.00022), xDir=(-1.0, 0.00109, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77924, 0.34611)
loop_1 = loop_1.lineTo(0.76546, 0.34182)
loop_1 = loop_1.lineTo(0.76474, 0.31375)
loop_1 = loop_1.lineTo(0.76289, 0.00697)
loop_1 = loop_1.lineTo(0.76337, -0.24644)
loop_1 = loop_1.lineTo(0.76348, -0.28521)
loop_1 = loop_1.lineTo(0.76134, -0.29534)
loop_1 = loop_1.lineTo(0.75826, -0.30584)
loop_1 = loop_1.lineTo(0.77243, -0.30981)
loop_1 = loop_1.lineTo(0.78052, -0.28234)
loop_1 = loop_1.threePointArc((0.78068, -0.25444), (0.78024, -0.22765))
loop_1 = loop_1.lineTo(0.77993, -0.1739)
loop_1 = loop_1.threePointArc((0.77957, -0.03539), (0.77981, 0.10499))
loop_1 = loop_1.threePointArc((0.78004, 0.16554), (0.78183, 0.22653))
loop_1 = loop_1.threePointArc((0.78187, 0.24719), (0.78192, 0.26073))
loop_1 = loop_1.threePointArc((0.78344, 0.29173), (0.78513, 0.31732))
loop_1 = loop_1.lineTo(0.77924, 0.34611)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_5_interval_0.stl')