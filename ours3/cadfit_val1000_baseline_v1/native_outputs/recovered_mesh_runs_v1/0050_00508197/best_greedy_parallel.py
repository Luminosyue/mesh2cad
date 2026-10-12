import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, -0.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-1.0, -0.01425)
sketch_1 = sketch_1.lineTo(-1.0, -0.04977)
sketch_1 = sketch_1.lineTo(-0.87014, -0.04845)
sketch_1 = sketch_1.lineTo(-0.87014, -0.01923)
sketch_1 = sketch_1.lineTo(1.0, -0.01425)
sketch_1 = sketch_1.lineTo(-0.99864, -0.01425)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.013000000000000001, 0.001, 0.001), axisEnd=(-1.0130000000000001, 0.001, 0.001))

result = solid_revolve_1