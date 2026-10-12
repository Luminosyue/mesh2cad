import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22247, 0.95671)
loop_1 = loop_1.threePointArc((0.21675, 0.94559), (0.21152, 0.93478))
loop_1 = loop_1.threePointArc((0.21166, 0.92137), (0.21117, 0.9077))
loop_1 = loop_1.threePointArc((0.2116, 0.89455), (0.21253, 0.88216))
loop_1 = loop_1.threePointArc((0.21384, 0.85622), (0.21549, 0.83156))
loop_1 = loop_1.threePointArc((0.2156, 0.82083), (0.21611, 0.81076))
loop_1 = loop_1.threePointArc((0.2165, 0.80158), (0.21653, 0.79222))
loop_1 = loop_1.lineTo(0.21657, 0.77987)
loop_1 = loop_1.lineTo(0.21793, 0.75154)
loop_1 = loop_1.threePointArc((0.21821, 0.7295), (0.21816, 0.70677))
loop_1 = loop_1.lineTo(0.21861, 0.67822)
loop_1 = loop_1.lineTo(0.22146, 0.6527)
loop_1 = loop_1.lineTo(0.22246, 0.63541)
loop_1 = loop_1.lineTo(0.22246, 0.9565)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_52_interval_0.stl')