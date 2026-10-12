import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43085, -0.85771, 0.03368), normal=(0.48756, 0.87304, -0.00905), xDir=(0.87308, -0.48758, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23891, 0.18898)
loop_1 = loop_1.lineTo(-0.32215, 0.18898)
loop_1 = loop_1.lineTo(-0.32604, -0.20103)
loop_1 = loop_1.lineTo(0.23817, -0.20103)
loop_1 = loop_1.lineTo(0.23889, 0.17935)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.78)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_3_interval_0.stl')