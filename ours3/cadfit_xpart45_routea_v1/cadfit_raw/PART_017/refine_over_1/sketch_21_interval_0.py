import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00628, -0.40589, 0.74061), normal=(0.0008, 0.92144, 0.38851), xDir=(1.0, -0.00087, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.38268, 0.00932)
loop_1 = loop_1.lineTo(0.37097, -0.00769)
loop_1 = loop_1.threePointArc((0.35271, -0.02978), (0.3358, -0.04988))
loop_1 = loop_1.lineTo(0.30037, -0.07353)
loop_1 = loop_1.lineTo(0.2731, -0.09155)
loop_1 = loop_1.lineTo(0.25646, -0.10038)
loop_1 = loop_1.lineTo(0.23956, -0.10769)
loop_1 = loop_1.lineTo(0.21802, -0.11948)
loop_1 = loop_1.lineTo(0.20723, -0.12398)
loop_1 = loop_1.threePointArc((0.19226, -0.13216), (0.17937, -0.13856))
loop_1 = loop_1.lineTo(0.38617, -0.14292)
loop_1 = loop_1.lineTo(0.38612, 0.01)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_21_interval_0.stl')