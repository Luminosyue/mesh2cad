import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.9525, 0.9525)
loop_1 = loop_1.lineTo(-0.94742, -0.9525)
loop_1 = loop_1.lineTo(0.9525, -0.94744)
loop_1 = loop_1.lineTo(0.94996, -0.5525)
loop_1 = loop_1.lineTo(-0.5525, -0.54742)
loop_1 = loop_1.lineTo(-0.55756, 0.9525)
loop_1 = loop_1.lineTo(-0.94997, 0.9525)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
