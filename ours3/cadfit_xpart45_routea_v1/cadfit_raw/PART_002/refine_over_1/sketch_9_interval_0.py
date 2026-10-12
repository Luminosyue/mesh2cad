import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00755, 0.02886, 0.69457), normal=(-9e-05, 0.35911, 0.9333), xDir=(0.0, 0.9333, -0.35911))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.42821, -0.26756)
loop_1 = loop_1.lineTo(-0.44278, -0.23653)
loop_1 = loop_1.lineTo(-0.44776, -0.22336)
loop_1 = loop_1.lineTo(-0.45912, -0.19309)
loop_1 = loop_1.lineTo(-0.46101, -0.18241)
loop_1 = loop_1.lineTo(-0.46341, -0.16385)
loop_1 = loop_1.threePointArc((-0.46488, -0.15441), (-0.46606, -0.14724))
loop_1 = loop_1.lineTo(-0.4689, -0.10638)
loop_1 = loop_1.lineTo(-0.46925, -0.26756)
loop_1 = loop_1.lineTo(-0.42974, -0.26756)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_9_interval_0.stl')