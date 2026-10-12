import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.5, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.375, 1.0)
loop_1 = loop_1.lineTo(-0.125, 0.99817)
loop_1 = loop_1.lineTo(-0.12134, -0.75)
loop_1 = loop_1.lineTo(0.375, -0.75184)
loop_1 = loop_1.lineTo(0.37317, -1.0)
loop_1 = loop_1.lineTo(-0.375, -0.99633)
loop_1 = loop_1.lineTo(-0.375, 0.99817)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.0)

result = solid_1
