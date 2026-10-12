import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.18071), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18135, -0.02705)
loop_1 = loop_1.lineTo(-0.1684, -0.04023)
loop_1 = loop_1.lineTo(-0.15619, -0.05632)
loop_1 = loop_1.lineTo(-0.13831, -0.05843)
loop_1 = loop_1.lineTo(-0.10765, -0.06652)
loop_1 = loop_1.lineTo(-0.0756, -0.04371)
loop_1 = loop_1.lineTo(-0.05909, -0.03034)
loop_1 = loop_1.lineTo(-0.05943, -0.01082)
loop_1 = loop_1.lineTo(-0.06976, 0.01159)
loop_1 = loop_1.lineTo(-0.07081, 0.02161)
loop_1 = loop_1.lineTo(-0.09651, 0.03812)
loop_1 = loop_1.lineTo(-0.1081, 0.04575)
loop_1 = loop_1.threePointArc((-0.13193, 0.04366), (-0.15664, 0.04172))
loop_1 = loop_1.lineTo(-0.17903, 0.02129)
loop_1 = loop_1.lineTo(-0.17982, -0.00417)
loop_1 = loop_1.lineTo(-0.18134, -0.02692)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_021/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_021/sketch_20_interval_0.stl')