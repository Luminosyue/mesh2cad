import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.89873, -0.23513, 0.01319), normal=(0.99267, 0.12086, 0.00046), xDir=(0.12086, -0.99267, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30676, -0.44599)
loop_1 = loop_1.lineTo(-0.32113, -0.44894)
loop_1 = loop_1.lineTo(-0.33001, -0.04974)
loop_1 = loop_1.lineTo(-0.31958, -0.05951)
loop_1 = loop_1.lineTo(-0.30198, -0.07351)
loop_1 = loop_1.lineTo(-0.2917, -0.08061)
loop_1 = loop_1.lineTo(-0.29862, -0.09366)
loop_1 = loop_1.lineTo(-0.28231, -0.44383)
loop_1 = loop_1.lineTo(-0.25545, -0.45284)
loop_1 = loop_1.lineTo(-0.30677, -0.45284)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_46_interval_0.stl')