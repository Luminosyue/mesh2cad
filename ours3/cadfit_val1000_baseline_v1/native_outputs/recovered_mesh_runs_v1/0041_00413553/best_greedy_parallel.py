import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.88143, 0.186, -0.0098), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.186, 0.07893)
loop_1 = loop_1.lineTo(1.186, 0.01067)
loop_1 = loop_1.lineTo(0.27133, 0.01067)
loop_1 = loop_1.lineTo(0.27133, -0.09855)
loop_1 = loop_1.lineTo(-0.814, -0.09855)
loop_1 = loop_1.lineTo(-0.814, 0.01067)
loop_1 = loop_1.lineTo(-0.69113, 0.01067)
loop_1 = loop_1.lineTo(-0.69113, 0.07893)
loop_1 = loop_1.lineTo(1.16425, 0.07893)
loop_1 = loop_1.lineTo(1.186, 0.07893)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.82)

result = solid_1