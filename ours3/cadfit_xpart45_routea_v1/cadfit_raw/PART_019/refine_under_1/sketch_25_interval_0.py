import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.82901, -0.04774, 0.50635), normal=(0.87431, -0.00024, -0.48537), xDir=(-0.00027, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.73251, 0.20434)
loop_1 = loop_1.lineTo(0.73689, 0.16089)
loop_1 = loop_1.lineTo(0.74557, 0.1071)
loop_1 = loop_1.lineTo(0.74768, 0.09033)
loop_1 = loop_1.lineTo(0.74774, 0.07779)
loop_1 = loop_1.lineTo(0.74451, 0.02482)
loop_1 = loop_1.lineTo(0.74871, -0.04439)
loop_1 = loop_1.lineTo(0.74855, -0.06288)
loop_1 = loop_1.lineTo(0.74537, -0.10856)
loop_1 = loop_1.lineTo(0.7449, -0.12133)
loop_1 = loop_1.lineTo(0.73927, -0.17148)
loop_1 = loop_1.lineTo(0.73593, -0.19188)
loop_1 = loop_1.lineTo(0.73304, -0.2024)
loop_1 = loop_1.lineTo(0.73252, 0.19948)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_25_interval_0.stl')