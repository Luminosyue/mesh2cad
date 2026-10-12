import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, 0.0, -0.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-0.33333, 0.91667)
sketch_1 = sketch_1.lineTo(-0.33178, 0.5)
sketch_1 = sketch_1.lineTo(0.33333, 0.50156)
sketch_1 = sketch_1.lineTo(0.33178, 1.0)
sketch_1 = sketch_1.lineTo(-0.16667, 0.99844)
sketch_1 = sketch_1.lineTo(-0.16745, 0.91667)
sketch_1 = sketch_1.lineTo(-0.33255, 0.91667)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.007, 0.001, 0.001), axisEnd=(1.007, 0.001, 0.001))

result = solid_revolve_1