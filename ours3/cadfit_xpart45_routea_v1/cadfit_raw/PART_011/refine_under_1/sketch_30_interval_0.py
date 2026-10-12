import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00738, -0.03777, 0.29585), normal=(0.00929, 0.04277, -0.99904), xDir=(0.0, -0.99908, -0.04277))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06059, 0.02607)
loop_1 = loop_1.lineTo(0.06102, 0.01149)
loop_1 = loop_1.lineTo(0.05837, -0.0169)
loop_1 = loop_1.lineTo(0.05921, -0.03662)
loop_1 = loop_1.threePointArc((0.05554, -0.07488), (0.05334, -0.10805))
loop_1 = loop_1.lineTo(0.05004, -0.13283)
loop_1 = loop_1.threePointArc((0.04942, -0.15842), (0.04831, -0.18093))
loop_1 = loop_1.lineTo(0.04594, -0.19699)
loop_1 = loop_1.lineTo(0.04453, -0.22904)
loop_1 = loop_1.lineTo(0.04326, -0.24243)
loop_1 = loop_1.lineTo(0.03774, -0.27715)
loop_1 = loop_1.lineTo(0.03835, -0.2897)
loop_1 = loop_1.lineTo(0.03863, -0.32526)
loop_1 = loop_1.lineTo(0.03652, -0.33681)
loop_1 = loop_1.lineTo(0.02981, -0.36899)
loop_1 = loop_1.lineTo(0.0603, 0.02238)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_30_interval_0.stl')