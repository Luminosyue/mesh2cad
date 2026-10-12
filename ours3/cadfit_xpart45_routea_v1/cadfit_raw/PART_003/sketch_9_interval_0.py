import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00469, 0.1208, 0.03775), normal=(-0.2658, -0.01154, -0.96396), xDir=(0.0, -0.99993, 0.01197))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.09509, -0.08123)
loop_1 = loop_1.threePointArc((1.08914, -0.07847), (1.08337, -0.07595))
loop_1 = loop_1.lineTo(1.07016, -0.07582)
loop_1 = loop_1.lineTo(1.05988, -0.07707)
loop_1 = loop_1.lineTo(1.01057, -0.06081)
loop_1 = loop_1.threePointArc((1.0002, -0.06208), (0.98936, -0.06311))
loop_1 = loop_1.lineTo(0.91887, -0.03848)
loop_1 = loop_1.lineTo(0.93083, -0.03657)
loop_1 = loop_1.lineTo(0.98013, -0.01876)
loop_1 = loop_1.threePointArc((0.99211, -0.02005), (1.00362, -0.02112))
loop_1 = loop_1.lineTo(1.03904, -0.01433)
loop_1 = loop_1.lineTo(1.06011, -0.00575)
loop_1 = loop_1.lineTo(1.07185, -0.00723)
loop_1 = loop_1.lineTo(1.0836, -0.0065)
loop_1 = loop_1.lineTo(1.09536, -0.0017)
loop_1 = loop_1.lineTo(1.1071, -0.00308)
loop_1 = loop_1.lineTo(1.09509, -0.08123)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_9_interval_0.stl')