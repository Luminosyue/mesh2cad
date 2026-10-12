import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-3e-05, -0.95238)
sketch_1 = sketch_1.lineTo(-0.1619, -0.95409)
sketch_1 = sketch_1.lineTo(-0.1619, -1.0)
sketch_1 = sketch_1.lineTo(-0.2381, -1.0)
sketch_1 = sketch_1.lineTo(-0.23809, -0.90476)
sketch_1 = sketch_1.lineTo(-0.1734, -0.90476)
sketch_1 = sketch_1.lineTo(-0.16945, 1.0)
sketch_1 = sketch_1.lineTo(-3e-05, 1.0)
sketch_1 = sketch_1.lineTo(-3e-05, -0.95238)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, -0.064, 0.001), axisEnd=(0.001, 0.936, 0.001))

result = solid_revolve_1