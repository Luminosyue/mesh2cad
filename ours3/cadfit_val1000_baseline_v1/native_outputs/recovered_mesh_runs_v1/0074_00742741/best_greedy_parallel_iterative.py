import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.84, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.90644)
loop_1 = loop_1.lineTo(1.0, 0.90166)
loop_1 = loop_1.lineTo(0.99625, -0.5449)
loop_1 = loop_1.lineTo(0.53806, -0.90644)
loop_1 = loop_1.lineTo(-0.63311, -0.9031)
loop_1 = loop_1.lineTo(-1.0, -0.53714)
loop_1 = loop_1.lineTo(-1.0, 0.90405)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.68)

result = solid_1
