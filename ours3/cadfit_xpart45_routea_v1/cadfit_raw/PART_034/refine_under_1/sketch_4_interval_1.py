import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.40289, 0.63519, 0.0182), normal=(0.48756, 0.87304, -0.00905), xDir=(0.87308, -0.48758, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34149, 0.15922)
loop_1 = loop_1.lineTo(0.35314, 0.14008)
loop_1 = loop_1.lineTo(0.35537, 0.12819)
loop_1 = loop_1.lineTo(0.36073, 0.09112)
loop_1 = loop_1.lineTo(0.36263, 0.03856)
loop_1 = loop_1.lineTo(0.3617, -0.00681)
loop_1 = loop_1.threePointArc((0.3581, -0.06203), (0.35489, -0.10566))
loop_1 = loop_1.lineTo(0.35311, -0.11706)
loop_1 = loop_1.lineTo(0.34854, -0.14167)
loop_1 = loop_1.lineTo(0.34156, 0.15621)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_4_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_4_interval_1.stl')