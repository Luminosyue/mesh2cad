import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.46759, 0.07179, -0.7315), normal=(0.58742, 0.00073, -0.80928), xDir=(0.00124, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.79782, 0.27862)
loop_1 = loop_1.lineTo(-0.65217, 0.27438)
loop_1 = loop_1.lineTo(-0.65157, -0.32606)
loop_1 = loop_1.lineTo(0.79843, -0.32362)
loop_1 = loop_1.lineTo(0.79784, 0.2584)
loop_1 = loop_1.lineTo(0.79782, 0.27862)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_11_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_11_interval_2.stl')