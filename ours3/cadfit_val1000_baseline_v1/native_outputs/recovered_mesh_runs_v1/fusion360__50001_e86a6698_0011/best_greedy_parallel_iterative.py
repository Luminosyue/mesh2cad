import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-9e-05, 1.0)
sketch_1 = sketch_1.lineTo(-0.8, 0.9976)
sketch_1 = sketch_1.lineTo(-0.79759, 0.2)
sketch_1 = sketch_1.lineTo(-0.39892, 0.1976)
sketch_1 = sketch_1.lineTo(-0.39598, -1.0)
sketch_1 = sketch_1.lineTo(-9e-05, -1.0)
sketch_1 = sketch_1.lineTo(-9e-05, 1.0)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.135, 0.001), axisEnd=(0.001, 1.1349999999999998, 0.001))
