import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05641, -0.49, 0.13142), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.96312, 0.24447)
loop_1 = loop_1.lineTo(-0.9632, 0.13082)
loop_1 = loop_1.lineTo(-0.96303, -0.08463)
loop_1 = loop_1.threePointArc((-0.96284, -0.05699), (-0.96286, -0.03263))
loop_1 = loop_1.lineTo(-0.96089, -0.01091)
loop_1 = loop_1.lineTo(-0.95706, 0.01938)
loop_1 = loop_1.lineTo(-0.9481, 0.0315)
loop_1 = loop_1.lineTo(-0.93777, 0.04093)
loop_1 = loop_1.lineTo(-0.89609, 0.06822)
loop_1 = loop_1.lineTo(-0.89828, 0.12339)
loop_1 = loop_1.lineTo(-0.93597, 0.1754)
loop_1 = loop_1.lineTo(-0.9481, 0.20261)
loop_1 = loop_1.lineTo(-0.95852, 0.22741)
loop_1 = loop_1.lineTo(-0.9613, 0.23774)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_53_interval_0.stl')