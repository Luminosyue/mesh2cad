import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0379, 0.01355, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11355, 0.1379)
loop_1 = loop_1.lineTo(-0.11355, -0.0621)
loop_1 = loop_1.lineTo(0.08645, -0.0621)
loop_1 = loop_1.lineTo(0.08645, 0.1379)
loop_1 = loop_1.lineTo(-0.10957, 0.1379)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.01355, 0.0379)
loop_2 = loop_2.circle(0.08398)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1