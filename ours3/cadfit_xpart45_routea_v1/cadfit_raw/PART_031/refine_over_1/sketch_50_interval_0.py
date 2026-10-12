import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.85825, -0.10839, 0.12758), normal=(0.78435, -4e-05, 0.62032), xDir=(-6e-05, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.29445, -0.09248)
loop_1 = loop_1.lineTo(0.31002, -0.12456)
loop_1 = loop_1.lineTo(0.33839, -0.14505)
loop_1 = loop_1.lineTo(0.35937, -0.15026)
loop_1 = loop_1.lineTo(0.38698, -0.15818)
loop_1 = loop_1.lineTo(-0.38714, -0.15772)
loop_1 = loop_1.lineTo(-0.36815, -0.15592)
loop_1 = loop_1.lineTo(-0.34328, -0.14449)
loop_1 = loop_1.lineTo(-0.31955, -0.12462)
loop_1 = loop_1.lineTo(-0.30641, -0.09761)
loop_1 = loop_1.lineTo(0.29348, -0.09248)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_50_interval_0.stl')