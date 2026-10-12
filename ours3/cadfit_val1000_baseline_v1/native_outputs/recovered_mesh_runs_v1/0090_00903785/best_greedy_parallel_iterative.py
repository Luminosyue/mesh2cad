import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.13875, 0.25065)
loop_1 = loop_1.lineTo(-0.13771, -0.25065)
loop_1 = loop_1.lineTo(0.13875, -0.24961)
loop_1 = loop_1.lineTo(0.13771, 0.25065)
loop_1 = loop_1.lineTo(-0.13823, 0.25065)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
