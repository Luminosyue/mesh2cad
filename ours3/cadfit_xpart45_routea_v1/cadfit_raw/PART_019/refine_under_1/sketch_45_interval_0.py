import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14571, 0.1041, -0.90357), normal=(0.15066, -0.00105, 0.98858), xDir=(-0.0, 1.0, 0.00106))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.59733, -0.49158)
loop_1 = loop_1.lineTo(0.61769, -0.4749)
loop_1 = loop_1.lineTo(-0.06102, -0.47297)
loop_1 = loop_1.lineTo(-0.04193, -0.47472)
loop_1 = loop_1.lineTo(-0.01299, -0.47507)
loop_1 = loop_1.threePointArc((0.01736, -0.47476), (0.04215, -0.47508))
loop_1 = loop_1.threePointArc((0.07576, -0.47424), (0.10384, -0.47383))
loop_1 = loop_1.lineTo(0.14208, -0.47577)
loop_1 = loop_1.lineTo(0.16552, -0.47515)
loop_1 = loop_1.threePointArc((0.21961, -0.47648), (0.26551, -0.47562))
loop_1 = loop_1.lineTo(0.29636, -0.47591)
loop_1 = loop_1.threePointArc((0.38053, -0.47789), (0.45418, -0.4788))
loop_1 = loop_1.lineTo(0.48023, -0.48056)
loop_1 = loop_1.threePointArc((0.51156, -0.48316), (0.53564, -0.48474))
loop_1 = loop_1.lineTo(0.56073, -0.48907)
loop_1 = loop_1.lineTo(0.59001, -0.49108)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_45_interval_0.stl')