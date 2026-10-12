import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-0.01517, 0.99912)
sketch_1 = sketch_1.lineTo(-0.32294, 0.99806)
sketch_1 = sketch_1.lineTo(-0.33285, 0.98709)
sketch_1 = sketch_1.threePointArc((-0.33543, 0.97472), (-0.33505, 0.96258))
sketch_1 = sketch_1.lineTo(-0.33024, 0.28678)
sketch_1 = sketch_1.threePointArc((-0.32757, 0.08875), (-0.32336, -0.09976))
sketch_1 = sketch_1.lineTo(-0.32456, -0.20971)
sketch_1 = sketch_1.lineTo(-0.33498, -0.21901)
sketch_1 = sketch_1.lineTo(-0.374, -0.21941)
sketch_1 = sketch_1.lineTo(-0.39075, -0.22301)
sketch_1 = sketch_1.threePointArc((-0.40489, -0.23235), (-0.41405, -0.24388))
sketch_1 = sketch_1.threePointArc((-0.41831, -0.25743), (-0.41788, -0.2694))
sketch_1 = sketch_1.threePointArc((-0.41077, -0.33342), (-0.40088, -0.39271))
sketch_1 = sketch_1.threePointArc((-0.39098, -0.41419), (-0.37806, -0.43053))
sketch_1 = sketch_1.threePointArc((-0.36352, -0.44092), (-0.34918, -0.44705))
sketch_1 = sketch_1.threePointArc((-0.34136, -0.45467), (-0.3365, -0.46317))
sketch_1 = sketch_1.threePointArc((-0.32835, -0.4774), (-0.323, -0.49156))
sketch_1 = sketch_1.threePointArc((-0.27976, -0.58968), (-0.2377, -0.68154))
sketch_1 = sketch_1.lineTo(-0.1604, -0.85632)
sketch_1 = sketch_1.lineTo(-0.13883, -0.90643)
sketch_1 = sketch_1.threePointArc((-0.07933, -0.97456), (0.00227, -0.99944))
sketch_1 = sketch_1.lineTo(-0.01517, 0.99912)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.006, 0.07, 0.001), axisEnd=(-0.015, 1.0699999999999998, 0.001))

result = solid_revolve_1