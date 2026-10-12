import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12841, 0.86295, -0.01306), normal=(0.00014, -0.99998, 0.00576), xDir=(-1.0, -0.00014, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.51376, -0.25763)
loop_1 = loop_1.lineTo(0.47414, -0.26033)
loop_1 = loop_1.threePointArc((0.44055, -0.26225), (0.41436, -0.26296))
loop_1 = loop_1.lineTo(0.37514, -0.26342)
loop_1 = loop_1.lineTo(0.32429, -0.26178)
loop_1 = loop_1.lineTo(0.28059, -0.26207)
loop_1 = loop_1.lineTo(0.23343, -0.26559)
loop_1 = loop_1.lineTo(0.52151, -0.26611)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_7_interval_0.stl')