import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.00373, -0.29607, -0.09756), normal=(0.97024, 0.24204, 0.00687), xDir=(0.24205, -0.97026, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19283, 0.45178)
loop_1 = loop_1.threePointArc((0.1808, 0.44827), (0.16936, 0.4445))
loop_1 = loop_1.lineTo(0.14268, 0.43516)
loop_1 = loop_1.threePointArc((0.12148, 0.42618), (0.10662, 0.41891))
loop_1 = loop_1.lineTo(0.08063, 0.38066)
loop_1 = loop_1.lineTo(0.07174, 0.27032)
loop_1 = loop_1.lineTo(0.06731, 0.16364)
loop_1 = loop_1.lineTo(0.06699, 0.05865)
loop_1 = loop_1.lineTo(0.11006, 0.00852)
loop_1 = loop_1.lineTo(0.12809, -0.00233)
loop_1 = loop_1.threePointArc((0.16247, -0.02002), (0.19204, -0.03299))
loop_1 = loop_1.lineTo(0.19283, 0.45065)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_25_interval_0.stl')