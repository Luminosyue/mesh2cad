import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32013, -0.26727, 0.09447), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04913, -0.30132)
loop_1 = loop_1.lineTo(0.05939, -0.30845)
loop_1 = loop_1.lineTo(0.07583, -0.32066)
loop_1 = loop_1.lineTo(0.09844, -0.33486)
loop_1 = loop_1.threePointArc((0.10832, -0.34135), (0.11662, -0.34656))
loop_1 = loop_1.lineTo(0.1351, -0.3594)
loop_1 = loop_1.lineTo(0.15569, -0.37035)
loop_1 = loop_1.lineTo(0.12887, -0.35034)
loop_1 = loop_1.lineTo(0.11794, -0.34511)
loop_1 = loop_1.lineTo(0.10744, -0.30406)
loop_1 = loop_1.lineTo(0.0759, -0.29944)
loop_1 = loop_1.lineTo(0.05937, -0.29949)
loop_1 = loop_1.lineTo(0.04933, -0.30007)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_1_interval_0.stl')