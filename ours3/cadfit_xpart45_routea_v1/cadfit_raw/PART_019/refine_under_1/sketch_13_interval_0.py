import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.82157, 0.00449, 0.50609), normal=(0.87312, -0.00073, -0.4875), xDir=(-0.00084, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78471, 0.29067)
loop_1 = loop_1.lineTo(0.79587, 0.259)
loop_1 = loop_1.lineTo(0.79835, 0.22029)
loop_1 = loop_1.lineTo(0.80627, 0.17137)
loop_1 = loop_1.lineTo(0.80829, 0.14878)
loop_1 = loop_1.lineTo(0.81099, 0.13244)
loop_1 = loop_1.lineTo(0.81051, 0.07899)
loop_1 = loop_1.lineTo(0.81524, 0.01142)
loop_1 = loop_1.lineTo(0.81493, 0.00021)
loop_1 = loop_1.lineTo(0.81167, -0.06231)
loop_1 = loop_1.lineTo(0.8152, -0.12064)
loop_1 = loop_1.lineTo(0.81467, -0.14854)
loop_1 = loop_1.lineTo(0.80574, -0.20362)
loop_1 = loop_1.threePointArc((0.79641, -0.23786), (0.78782, -0.26738))
loop_1 = loop_1.lineTo(0.78471, 0.29066)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.94)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_13_interval_0.stl')