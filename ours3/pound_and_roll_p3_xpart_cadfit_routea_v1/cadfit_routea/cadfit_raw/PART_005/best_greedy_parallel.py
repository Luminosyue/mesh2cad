import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, -0.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.00781, -0.99932)
sketch_1 = sketch_1.threePointArc((0.05348, -0.99896), (0.09712, -0.99457))
sketch_1 = sketch_1.threePointArc((0.14364, -0.98862), (0.1856, -0.9792))
sketch_1 = sketch_1.threePointArc((0.25639, -0.96467), (0.32147, -0.94691))
sketch_1 = sketch_1.threePointArc((0.41122, -0.90617), (0.49305, -0.86277))
sketch_1 = sketch_1.threePointArc((0.64826, -0.74854), (0.76977, -0.61159))
sketch_1 = sketch_1.threePointArc((0.81298, -0.54616), (0.84951, -0.48091))
sketch_1 = sketch_1.threePointArc((0.87989, -0.4196), (0.90262, -0.36006))
sketch_1 = sketch_1.threePointArc((0.92907, -0.28798), (0.94708, -0.21862))
sketch_1 = sketch_1.threePointArc((0.96229, -0.14444), (0.96855, -0.07396))
sketch_1 = sketch_1.threePointArc((0.97392, 0.027), (0.96814, 0.12185))
sketch_1 = sketch_1.threePointArc((0.95956, 0.20072), (0.94657, 0.27374))
sketch_1 = sketch_1.threePointArc((0.9095, 0.39637), (0.86322, 0.50811))
sketch_1 = sketch_1.threePointArc((0.69318, 0.73842), (0.4736, 0.90042))
sketch_1 = sketch_1.threePointArc((0.38722, 0.93639), (0.30406, 0.9641))
sketch_1 = sketch_1.threePointArc((0.22733, 0.9804), (0.15473, 0.99064))
sketch_1 = sketch_1.threePointArc((0.0769, 0.99884), (0.00369, 0.99953))
sketch_1 = sketch_1.lineTo(0.00781, -0.99932)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.007, 0.009000000000000001, 0.001), axisEnd=(0.009000000000000001, -0.991, 0.001))

result = solid_revolve_1