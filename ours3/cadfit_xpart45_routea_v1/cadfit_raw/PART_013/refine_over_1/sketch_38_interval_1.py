import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.4485, 0.41847, 0.04412), normal=(-0.61375, 0.7895, 0.00198), xDir=(0.7895, 0.61375, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01435, -0.28925)
loop_1 = loop_1.lineTo(-0.00603, -0.28973)
loop_1 = loop_1.lineTo(-0.00606, -0.3116)
loop_1 = loop_1.threePointArc((-1e-05, -0.3113), (0.00487, -0.31113))
loop_1 = loop_1.lineTo(0.01803, -0.31098)
loop_1 = loop_1.lineTo(0.02985, -0.3112)
loop_1 = loop_1.lineTo(0.07934, -0.29553)
loop_1 = loop_1.lineTo(0.09638, -0.28606)
loop_1 = loop_1.lineTo(0.10801, -0.27905)
loop_1 = loop_1.lineTo(0.01869, -0.28752)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_38_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_38_interval_1.stl')