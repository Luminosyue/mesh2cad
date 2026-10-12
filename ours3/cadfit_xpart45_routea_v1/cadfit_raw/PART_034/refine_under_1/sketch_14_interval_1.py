import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06282, 0.73223, 0.00924), normal=(-0.06485, 0.99785, -0.00971), xDir=(0.99789, 0.06485, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35455, 0.15654)
loop_1 = loop_1.lineTo(0.36789, 0.13194)
loop_1 = loop_1.threePointArc((0.36801, 0.11752), (0.3681, 0.10634))
loop_1 = loop_1.lineTo(0.36948, 0.08297)
loop_1 = loop_1.lineTo(0.36544, 0.03118)
loop_1 = loop_1.threePointArc((0.36431, 0.00627), (0.36377, -0.01495))
loop_1 = loop_1.lineTo(0.36315, -0.03329)
loop_1 = loop_1.lineTo(0.36344, -0.06392)
loop_1 = loop_1.lineTo(0.36231, -0.08139)
loop_1 = loop_1.lineTo(0.36276, -0.11288)
loop_1 = loop_1.lineTo(0.36133, -0.12934)
loop_1 = loop_1.lineTo(0.35461, 0.15367)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_14_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_14_interval_1.stl')