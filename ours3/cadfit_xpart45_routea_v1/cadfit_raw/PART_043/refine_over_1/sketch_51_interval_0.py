import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.39278), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30576, -0.55484)
loop_1 = loop_1.lineTo(0.32326, -0.57134)
loop_1 = loop_1.threePointArc((0.33148, -0.57951), (0.33972, -0.5881))
loop_1 = loop_1.lineTo(0.35422, -0.60002)
loop_1 = loop_1.lineTo(0.36544, -0.60814)
loop_1 = loop_1.lineTo(0.39124, -0.61586)
loop_1 = loop_1.lineTo(0.40291, -0.61429)
loop_1 = loop_1.lineTo(0.41779, -0.6106)
loop_1 = loop_1.threePointArc((0.43009, -0.60629), (0.44163, -0.60189))
loop_1 = loop_1.lineTo(0.46145, -0.58969)
loop_1 = loop_1.threePointArc((0.47499, -0.57426), (0.47955, -0.56637))
loop_1 = loop_1.lineTo(0.48514, -0.55609)
loop_1 = loop_1.lineTo(0.49346, -0.53342)
loop_1 = loop_1.lineTo(0.49852, -0.50364)
loop_1 = loop_1.lineTo(0.50006, -0.48826)
loop_1 = loop_1.lineTo(0.30592, -0.55479)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_51_interval_0.stl')