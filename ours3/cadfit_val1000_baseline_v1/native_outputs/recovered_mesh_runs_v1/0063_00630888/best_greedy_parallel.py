import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.49), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.59318, 0.53333)
loop_1 = loop_1.lineTo(-0.58911, -0.53753)
loop_1 = loop_1.lineTo(-0.13628, -1.0)
loop_1 = loop_1.lineTo(0.59318, -0.99611)
loop_1 = loop_1.lineTo(0.58736, 1.0)
loop_1 = loop_1.lineTo(-0.14287, 0.99721)
loop_1 = loop_1.lineTo(-0.59182, 0.53473)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.98)

result = solid_1