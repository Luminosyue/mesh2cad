import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00557, 0.15119, -0.27362), normal=(0.02791, -0.62791, 0.77778), xDir=(-0.99901, -0.04441, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.27446, -0.07245)
loop_1 = loop_1.lineTo(0.27305, -0.08582)
loop_1 = loop_1.lineTo(0.25533, -0.11489)
loop_1 = loop_1.lineTo(0.23724, -0.122)
loop_1 = loop_1.threePointArc((0.20274, -0.12174), (0.16908, -0.12073))
loop_1 = loop_1.lineTo(0.15072, -0.11766)
loop_1 = loop_1.lineTo(0.13157, -0.10106)
loop_1 = loop_1.lineTo(0.12335, -0.07767)
loop_1 = loop_1.lineTo(0.12196, -0.05726)
loop_1 = loop_1.lineTo(0.12223, -0.03606)
loop_1 = loop_1.lineTo(0.2729, -0.03463)
loop_1 = loop_1.threePointArc((0.27497, -0.04965), (0.27493, -0.06063))
loop_1 = loop_1.lineTo(0.27446, -0.07245)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_31_interval_0.stl')