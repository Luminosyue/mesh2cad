import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, 0.0, -0.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-0.2381, 0.00024)
sketch_1 = sketch_1.lineTo(-0.2381, -0.38095)
sketch_1 = sketch_1.lineTo(-1.0, -0.38095)
sketch_1 = sketch_1.lineTo(-1.0, -0.47492)
sketch_1 = sketch_1.lineTo(-0.2381, -0.47492)
sketch_1 = sketch_1.lineTo(-0.23809, -0.61905)
sketch_1 = sketch_1.lineTo(0.04762, -0.61905)
sketch_1 = sketch_1.lineTo(0.04763, -0.47619)
sketch_1 = sketch_1.lineTo(1.0, -0.47291)
sketch_1 = sketch_1.lineTo(0.99999, -0.38095)
sketch_1 = sketch_1.lineTo(0.04762, -0.37749)
sketch_1 = sketch_1.lineTo(0.04762, 0.00024)
sketch_1 = sketch_1.lineTo(-0.2381, 0.00024)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.015, 0.001, 0.001), axisEnd=(-1.0150000000000001, 0.001, 0.001))

result = solid_revolve_1