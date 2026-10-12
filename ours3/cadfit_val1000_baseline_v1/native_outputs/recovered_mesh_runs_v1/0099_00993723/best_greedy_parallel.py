import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.01006, -0.00694)
sketch_1 = sketch_1.lineTo(-0.99969, -0.00556)
sketch_1 = sketch_1.lineTo(-0.99969, 0.00694)
sketch_1 = sketch_1.lineTo(0.01006, 0.00694)
sketch_1 = sketch_1.lineTo(0.01006, -0.00694)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.011, 0.001, 0.001), axisEnd=(0.011, 1.001, 0.001))

result = solid_revolve_1