import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02598, 0.0032, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1032, 0.12598)
loop_1 = loop_1.lineTo(-0.1032, -0.07402)
loop_1 = loop_1.lineTo(0.0968, -0.07402)
loop_1 = loop_1.lineTo(0.0968, 0.12598)
loop_1 = loop_1.lineTo(-0.09922, 0.12598)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.0032, 0.02598)
loop_2 = loop_2.circle(0.08398)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1