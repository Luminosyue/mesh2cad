import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73213, 0.36594, 0.0023), normal=(-0.64804, 0.76146, 0.0152), xDir=(0.76154, 0.64811, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.2971, -0.05772)
loop_1 = loop_1.lineTo(0.29862, -0.06897)
loop_1 = loop_1.lineTo(0.29956, 0.24813)
loop_1 = loop_1.lineTo(0.28554, 0.24813)
loop_1 = loop_1.lineTo(0.28097, 0.01929)
loop_1 = loop_1.lineTo(0.28833, 0.03521)
loop_1 = loop_1.lineTo(0.29228, 0.05783)
loop_1 = loop_1.threePointArc((0.29265, 0.09353), (0.29367, 0.12606))
loop_1 = loop_1.lineTo(0.29322, -0.05224)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_17_interval_3.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_17_interval_3.stl')