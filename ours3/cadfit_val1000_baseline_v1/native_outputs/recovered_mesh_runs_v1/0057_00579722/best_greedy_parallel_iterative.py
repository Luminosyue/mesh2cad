import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.5), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.3, 1.0)
loop_1 = loop_1.lineTo(-0.29614, -1.0)
loop_1 = loop_1.lineTo(0.3, -0.99807)
loop_1 = loop_1.lineTo(0.29808, -0.78903)
loop_1 = loop_1.lineTo(0.0, -0.78709)
loop_1 = loop_1.lineTo(0.00384, 0.83292)
loop_1 = loop_1.lineTo(0.3, 0.83482)
loop_1 = loop_1.lineTo(0.29807, 1.0)
loop_1 = loop_1.lineTo(-0.29808, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.0)

result = solid_1
