import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02315, 0.09769, -0.00292), normal=(0.0, -1.0, 0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.02315, 0.45862)
loop_1 = loop_1.lineTo(-0.97685, 0.45862)
loop_1 = loop_1.lineTo(-0.97685, -0.46446)
loop_1 = loop_1.lineTo(1.02315, -0.46446)
loop_1 = loop_1.lineTo(1.02315, 0.43084)
loop_1 = loop_1.lineTo(1.02315, 0.45862)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.40777, -0.00292)
loop_2 = loop_2.circle(0.12278)
loop_3 = sketch_1.moveTo(0.70693, -0.30208)
loop_3 = loop_3.circle(0.04988)
loop_4 = sketch_1.moveTo(0.70693, 0.29624)
loop_4 = loop_4.circle(0.04988)
loop_5 = sketch_1.moveTo(0.10861, 0.29624)
loop_5 = loop_5.circle(0.04988)
loop_6 = sketch_1.moveTo(0.10861, -0.30208)
loop_6 = loop_6.circle(0.04988)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3).add(loop_4).add(loop_5).add(loop_6)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
