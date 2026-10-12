import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.00031, 0.45183)
sketch_1 = sketch_1.threePointArc((-0.2094, 0.45429), (-0.41074, 0.45453))
sketch_1 = sketch_1.threePointArc((-0.50553, 0.45656), (-0.60252, 0.46082))
sketch_1 = sketch_1.threePointArc((-0.75873, 0.46441), (-0.90709, 0.46522))
sketch_1 = sketch_1.lineTo(-0.91408, 0.38081)
sketch_1 = sketch_1.lineTo(-0.9172, 0.36985)
sketch_1 = sketch_1.lineTo(-0.97482, 0.34576)
sketch_1 = sketch_1.lineTo(-0.99037, 0.33208)
sketch_1 = sketch_1.threePointArc((-0.99554, 0.31859), (-0.99925, 0.30679))
sketch_1 = sketch_1.threePointArc((-0.9996, 0.28688), (-0.99807, 0.26994))
sketch_1 = sketch_1.threePointArc((-0.97826, 0.15156), (-0.94124, 0.04418))
sketch_1 = sketch_1.threePointArc((-0.92799, 0.01106), (-0.91257, -0.01764))
sketch_1 = sketch_1.lineTo(-0.88377, -0.07114)
sketch_1 = sketch_1.threePointArc((-0.84219, -0.12701), (-0.79997, -0.17677))
sketch_1 = sketch_1.threePointArc((-0.70744, -0.25919), (-0.61046, -0.32569))
sketch_1 = sketch_1.threePointArc((-0.59104, -0.33794), (-0.57297, -0.34735))
sketch_1 = sketch_1.threePointArc((-0.5033, -0.38177), (-0.43591, -0.40997))
sketch_1 = sketch_1.threePointArc((-0.3531, -0.43441), (-0.27389, -0.45247))
sketch_1 = sketch_1.threePointArc((-0.13197, -0.46818), (0.00341, -0.47311))
sketch_1 = sketch_1.lineTo(0.00031, 0.45183)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.003, 0.074, 0.001), axisEnd=(-0.001, 1.0739999999999998, 0.001))

result = solid_revolve_1