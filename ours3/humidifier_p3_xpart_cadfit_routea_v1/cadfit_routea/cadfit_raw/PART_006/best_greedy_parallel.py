import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-0.10477, 0.99973)
sketch_1 = sketch_1.threePointArc((-0.07563, 0.99934), (-0.0453, 0.99786))
sketch_1 = sketch_1.threePointArc((-0.03881, 0.99717), (-0.03279, 0.99718))
sketch_1 = sketch_1.threePointArc((-0.00931, 0.9942), (0.01473, 0.9901))
sketch_1 = sketch_1.threePointArc((0.03856, 0.9856), (0.06296, 0.98017))
sketch_1 = sketch_1.threePointArc((0.09141, 0.97383), (0.12063, 0.96662))
sketch_1 = sketch_1.lineTo(0.15294, 0.95851)
sketch_1 = sketch_1.lineTo(0.16991, 0.95118)
sketch_1 = sketch_1.lineTo(0.17723, 0.93993)
sketch_1 = sketch_1.lineTo(0.17091, 0.92761)
sketch_1 = sketch_1.threePointArc((0.16063, 0.92411), (0.15415, 0.92329))
sketch_1 = sketch_1.lineTo(0.12748, 0.93003)
sketch_1 = sketch_1.lineTo(0.08071, 0.94259)
sketch_1 = sketch_1.lineTo(0.04198, 0.95233)
sketch_1 = sketch_1.threePointArc((0.00904, 0.96021), (-0.02252, 0.96693))
sketch_1 = sketch_1.threePointArc((-0.03466, 0.96839), (-0.04613, 0.96885))
sketch_1 = sketch_1.threePointArc((-0.05659, 0.96926), (-0.06639, 0.96905))
sketch_1 = sketch_1.threePointArc((-0.11351, 0.96902), (-0.16232, 0.96918))
sketch_1 = sketch_1.lineTo(-0.17757, 0.97351)
sketch_1 = sketch_1.threePointArc((-0.18057, 0.98194), (-0.18216, 0.98826))
sketch_1 = sketch_1.lineTo(-0.16513, 0.99904)
sketch_1 = sketch_1.threePointArc((-0.13557, 0.99958), (-0.10504, 0.99975))
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.002, 0.001), axisEnd=(1.001, 0.002, 0.001))

result = solid_revolve_1