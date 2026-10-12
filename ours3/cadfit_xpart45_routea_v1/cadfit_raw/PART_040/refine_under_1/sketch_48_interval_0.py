import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.74669, -0.14692, 0.02533), normal=(0.5435, 0.83941, 0.00056), xDir=(0.83941, -0.5435, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32224, 0.16423)
loop_1 = loop_1.lineTo(0.3218, -0.09014)
loop_1 = loop_1.lineTo(0.32932, -0.07027)
loop_1 = loop_1.lineTo(0.33161, -0.05687)
loop_1 = loop_1.lineTo(0.33262, -0.03978)
loop_1 = loop_1.lineTo(0.3327, -0.02321)
loop_1 = loop_1.lineTo(0.33335, -0.00696)
loop_1 = loop_1.lineTo(0.33272, 0.02667)
loop_1 = loop_1.lineTo(0.33149, 0.04433)
loop_1 = loop_1.threePointArc((0.33228, 0.06126), (0.33326, 0.07623))
loop_1 = loop_1.threePointArc((0.33367, 0.09392), (0.33449, 0.10951))
loop_1 = loop_1.threePointArc((0.33188, 0.11929), (0.32999, 0.12614))
loop_1 = loop_1.lineTo(0.32346, 0.14278)
loop_1 = loop_1.lineTo(0.32224, 0.16423)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_48_interval_0.stl')