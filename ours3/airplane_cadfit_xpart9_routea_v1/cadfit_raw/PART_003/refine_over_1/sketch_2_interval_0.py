import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.68669, -0.06184, 0.1873), normal=(-0.11375, 0.00192, -0.99351), xDir=(0.0, -1.0, -0.00193))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08925, 0.23303)
loop_1 = loop_1.lineTo(-0.10353, 0.24839)
loop_1 = loop_1.lineTo(-0.11986, 0.26187)
loop_1 = loop_1.lineTo(-0.13849, 0.27293)
loop_1 = loop_1.lineTo(-0.15503, 0.28065)
loop_1 = loop_1.lineTo(-0.16562, 0.28379)
loop_1 = loop_1.threePointArc((-0.17452, 0.28593), (-0.18217, 0.28796))
loop_1 = loop_1.threePointArc((-0.19673, 0.29019), (-0.20173, 0.2903))
loop_1 = loop_1.lineTo(-0.08173, 0.29025)
loop_1 = loop_1.lineTo(-0.08171, 0.22478)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_2_interval_0.stl')