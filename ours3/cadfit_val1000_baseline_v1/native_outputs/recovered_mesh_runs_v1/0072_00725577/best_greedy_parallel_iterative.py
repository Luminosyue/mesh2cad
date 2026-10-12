import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.006, 0.14412, -0.03667), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.14412, 1.006)
loop_1 = loop_1.lineTo(-1.14412, -0.994)
loop_1 = loop_1.lineTo(0.85588, -0.994)
loop_1 = loop_1.lineTo(0.85588, 1.006)
loop_1 = loop_1.lineTo(-1.10245, 1.006)
loop_1 = loop_1.lineTo(-1.14412, 1.006)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.74412, 0.606)
loop_2 = loop_2.lineTo(0.45588, 0.606)
loop_2 = loop_2.lineTo(0.45588, -0.594)
loop_2 = loop_2.lineTo(-0.74412, -0.594)
loop_2 = loop_2.lineTo(-0.74412, 0.58232)
loop_2 = loop_2.lineTo(-0.74412, 0.606)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
