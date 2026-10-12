import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-0.26087, 0.34783)
sketch_1 = sketch_1.lineTo(-1.0, 0.34591)
sketch_1 = sketch_1.lineTo(-0.99904, 0.17391)
sketch_1 = sketch_1.lineTo(-0.86957, 0.17296)
sketch_1 = sketch_1.lineTo(-0.86765, -0.34783)
sketch_1 = sketch_1.lineTo(-0.26087, -0.34591)
sketch_1 = sketch_1.lineTo(-0.26087, 0.34687)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.025, 0.001), axisEnd=(0.001, 1.025, 0.001))

result = solid_revolve_1