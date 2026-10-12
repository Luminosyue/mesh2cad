import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04211, -0.83667, 0.08422), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16062, 0.43383)
loop_1 = loop_1.lineTo(-0.04211, 0.19355)
loop_1 = loop_1.lineTo(0.0764, 0.43383)
loop_1 = loop_1.lineTo(0.95789, 0.16463)
loop_1 = loop_1.lineTo(0.95789, -0.26538)
loop_1 = loop_1.lineTo(-1.04211, -0.26538)
loop_1 = loop_1.lineTo(-1.04211, 0.16463)
loop_1 = loop_1.lineTo(-0.18707, 0.42575)
loop_1 = loop_1.lineTo(-0.16062, 0.43383)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.18956, 0.3669)
loop_2 = loop_2.lineTo(-0.98655, 0.12351)
loop_2 = loop_2.lineTo(-0.98655, -0.20982)
loop_2 = loop_2.lineTo(0.90233, -0.20982)
loop_2 = loop_2.lineTo(0.90233, 0.12351)
loop_2 = loop_2.lineTo(0.10534, 0.3669)
loop_2 = loop_2.lineTo(-0.04211, 0.06795)
loop_2 = loop_2.lineTo(-0.17855, 0.3446)
loop_2 = loop_2.lineTo(-0.18956, 0.3669)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
