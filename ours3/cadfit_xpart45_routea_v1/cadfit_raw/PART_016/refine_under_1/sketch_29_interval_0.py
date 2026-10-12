import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.49852, -0.67765, -0.13034), normal=(0.63153, 0.77535, 0.00016), xDir=(0.77535, -0.63153, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.1963, 0.10179)
loop_1 = loop_1.lineTo(0.19634, -0.23821)
loop_1 = loop_1.lineTo(0.55467, -0.23821)
loop_1 = loop_1.lineTo(0.55472, 0.10179)
loop_1 = loop_1.lineTo(0.20349, 0.10179)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_29_interval_0.stl')