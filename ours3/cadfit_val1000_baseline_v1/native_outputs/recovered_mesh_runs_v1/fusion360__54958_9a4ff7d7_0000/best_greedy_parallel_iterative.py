import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.23579, 0.00054)
sketch_1 = sketch_1.lineTo(0.23389, -0.99927)
sketch_1 = sketch_1.lineTo(-0.23579, -0.99927)
sketch_1 = sketch_1.lineTo(-0.23579, -0.84912)
sketch_1 = sketch_1.lineTo(0.14147, -0.84912)
sketch_1 = sketch_1.lineTo(0.14147, 0.00054)
sketch_1 = sketch_1.lineTo(0.23579, 0.00054)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.107, 0.002, 0.001), axisEnd=(-0.893, 0.002, 0.001))
