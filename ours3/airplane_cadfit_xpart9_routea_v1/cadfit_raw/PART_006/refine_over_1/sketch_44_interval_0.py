import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.0432), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16439, -0.00898)
loop_1 = loop_1.lineTo(0.16729, -0.02774)
loop_1 = loop_1.threePointArc((0.16668, -0.04482), (0.1664, -0.06098))
loop_1 = loop_1.lineTo(0.23175, 0.27979)
loop_1 = loop_1.threePointArc((0.2214, 0.26078), (0.21214, 0.24244))
loop_1 = loop_1.lineTo(0.19744, 0.20768)
loop_1 = loop_1.lineTo(0.18829, 0.18656)
loop_1 = loop_1.threePointArc((0.18558, 0.17673), (0.1835, 0.1674))
loop_1 = loop_1.threePointArc((0.17707, 0.1568), (0.17146, 0.14663))
loop_1 = loop_1.lineTo(0.16685, 0.13198)
loop_1 = loop_1.lineTo(0.166, 0.10529)
loop_1 = loop_1.lineTo(0.16698, 0.08606)
loop_1 = loop_1.lineTo(0.16509, 0.0666)
loop_1 = loop_1.lineTo(0.16792, 0.05488)
loop_1 = loop_1.lineTo(0.16722, 0.03265)
loop_1 = loop_1.lineTo(0.16841, 0.01454)
loop_1 = loop_1.lineTo(0.16443, -0.00874)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_44_interval_0.stl')