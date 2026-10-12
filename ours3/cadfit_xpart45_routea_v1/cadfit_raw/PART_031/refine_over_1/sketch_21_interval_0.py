import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59366, -0.76348, -0.15318), normal=(0.71469, 0.69945, 0.00019), xDir=(0.69945, -0.71469, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24236, 0.39029)
loop_1 = loop_1.lineTo(0.22053, 0.43767)
loop_1 = loop_1.lineTo(0.22052, 0.40272)
loop_1 = loop_1.lineTo(0.24734, 0.3852)
loop_1 = loop_1.lineTo(0.2527, 0.37346)
loop_1 = loop_1.lineTo(0.26265, 0.34858)
loop_1 = loop_1.lineTo(0.26627, 0.3385)
loop_1 = loop_1.lineTo(0.27314, 0.28895)
loop_1 = loop_1.lineTo(0.27698, 0.19872)
loop_1 = loop_1.threePointArc((0.27833, 0.18369), (0.27919, 0.1712))
loop_1 = loop_1.lineTo(0.27912, 0.39029)
loop_1 = loop_1.lineTo(0.24515, 0.39029)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_21_interval_0.stl')