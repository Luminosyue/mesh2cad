import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19593, 0.14236)
loop_1 = loop_1.lineTo(0.4356, 0.47352)
loop_1 = loop_1.lineTo(0.35206, 0.40087)
loop_1 = loop_1.lineTo(0.28129, 0.31465)
loop_1 = loop_1.lineTo(0.22573, 0.21762)
loop_1 = loop_1.lineTo(0.19603, 0.14262)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)
plane_2 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.19593, 0.14236)
loop_1 = loop_1.lineTo(0.43559, 0.47352)
loop_1 = loop_1.lineTo(0.35206, 0.40087)
loop_1 = loop_1.lineTo(0.28129, 0.31465)
loop_1 = loop_1.lineTo(0.22574, 0.21762)
loop_1 = loop_1.lineTo(0.19603, 0.14261)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)