import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.84841, -0.39421, 0.15417), normal=(0.92641, 0.37652, -0.00019), xDir=(0.37652, -0.92641, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36325, -0.16033)
loop_1 = loop_1.lineTo(0.36316, -0.37598)
loop_1 = loop_1.lineTo(0.29199, -0.37598)
loop_1 = loop_1.lineTo(0.31487, -0.36856)
loop_1 = loop_1.threePointArc((0.32777, -0.35145), (0.33843, -0.33707))
loop_1 = loop_1.lineTo(0.34623, -0.32403)
loop_1 = loop_1.lineTo(0.34949, -0.31356)
loop_1 = loop_1.lineTo(0.35517, -0.26169)
loop_1 = loop_1.lineTo(0.36059, -0.20976)
loop_1 = loop_1.lineTo(0.36149, -0.19844)
loop_1 = loop_1.lineTo(0.36324, -0.16059)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_38_interval_0.stl')