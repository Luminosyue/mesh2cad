import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.66667), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66667, 1.0)
loop_1 = loop_1.lineTo(-0.66222, -1.0)
loop_1 = loop_1.lineTo(0.0, -0.99778)
loop_1 = loop_1.lineTo(0.00444, 0.33333)
loop_1 = loop_1.lineTo(0.66667, 0.33556)
loop_1 = loop_1.lineTo(0.66444, 1.0)
loop_1 = loop_1.lineTo(-0.66444, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
