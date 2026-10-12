import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.12)
loop_1 = loop_1.lineTo(0.9985, -0.0)
loop_1 = loop_1.lineTo(0.4, -0.003)
loop_1 = loop_1.lineTo(0.3985, -0.12)
loop_1 = loop_1.lineTo(-1.0, -0.11554)
loop_1 = loop_1.lineTo(-0.99851, 0.12)
loop_1 = loop_1.lineTo(0.99851, 0.12)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
