import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, -0.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.01809, 1e-05)
sketch_1 = sketch_1.lineTo(0.0042, -0.019)
sketch_1 = sketch_1.lineTo(-0.01809, -0.01168)
sketch_1 = sketch_1.lineTo(-0.01809, 1e-05)
sketch_1 = sketch_1.lineTo(0.01809, 1e-05)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.001, 0.001, 0.001), axisEnd=(-1.0010000000000001, 0.001, 0.001))

# Revolve operation 2
plane_1 = cq.Plane(origin=(0.0, 0.0, -0.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-1.0, 0.0)
sketch_1 = sketch_1.lineTo(-0.99995, -0.01809)
sketch_1 = sketch_1.lineTo(1.0, -0.01256)
sketch_1 = sketch_1.lineTo(1.0, 0.0)
sketch_1 = sketch_1.lineTo(-1.0, 0.0)
sketch_1 = sketch_1.close()
solid_revolve_2 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.0, 0.001, 0.001), axisEnd=(-0.9999999999999999, 0.001, 0.001))

result = solid_revolve_1
result = result.add(solid_revolve_2)