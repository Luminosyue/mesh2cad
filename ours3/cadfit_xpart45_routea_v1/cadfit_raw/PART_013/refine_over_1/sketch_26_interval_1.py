import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81423, -0.01499, 0.03414), normal=(-0.99345, 0.11429, 0.00217), xDir=(0.11429, 0.99345, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30915, 0.17516)
loop_1 = loop_1.lineTo(-0.25819, 0.17516)
loop_1 = loop_1.lineTo(-0.27536, 0.15897)
loop_1 = loop_1.lineTo(-0.28575, 0.14986)
loop_1 = loop_1.threePointArc((-0.29332, 0.14165), (-0.29939, 0.13484))
loop_1 = loop_1.lineTo(-0.30173, 0.08814)
loop_1 = loop_1.lineTo(-0.30831, 0.05033)
loop_1 = loop_1.lineTo(-0.30914, 0.17366)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_26_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_26_interval_1.stl')