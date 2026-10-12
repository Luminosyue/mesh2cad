import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.159, -0.34263, 0.01677), normal=(0.27474, 0.53531, 0.79873), xDir=(0.88966, -0.45662, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01915, 0.14094)
loop_1 = loop_1.lineTo(0.01765, 0.15335)
loop_1 = loop_1.lineTo(0.21125, 0.11812)
loop_1 = loop_1.lineTo(0.19875, 0.11948)
loop_1 = loop_1.lineTo(0.17859, 0.12186)
loop_1 = loop_1.lineTo(0.13614, 0.12555)
loop_1 = loop_1.threePointArc((0.12433, 0.12654), (0.11451, 0.12757))
loop_1 = loop_1.lineTo(0.02359, 0.13562)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_4_interval_0.stl')