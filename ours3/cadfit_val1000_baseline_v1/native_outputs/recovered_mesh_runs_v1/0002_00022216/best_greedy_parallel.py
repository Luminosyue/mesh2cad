import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00889, -1.0, -0.01846), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.10889, 0.08154)
loop_1 = loop_1.lineTo(-0.10889, -0.11846)
loop_1 = loop_1.lineTo(0.09111, -0.11846)
loop_1 = loop_1.lineTo(0.09111, 0.08154)
loop_1 = loop_1.lineTo(-0.10491, 0.08154)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.00889, -0.01846)
loop_2 = loop_2.circle(0.08398)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1