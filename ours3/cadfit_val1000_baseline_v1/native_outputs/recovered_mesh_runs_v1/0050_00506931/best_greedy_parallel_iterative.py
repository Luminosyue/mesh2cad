import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.16333, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66667, 0.99985)
loop_1 = loop_1.threePointArc((-0.9178, 0.88529), (-0.99836, 0.63218))
loop_1 = loop_1.lineTo(-0.99706, -0.70856)
loop_1 = loop_1.threePointArc((-0.86844, -0.93153), (-0.63217, -0.99839))
loop_1 = loop_1.lineTo(0.70856, -0.99706)
loop_1 = loop_1.threePointArc((0.93153, -0.86844), (0.99839, -0.63217))
loop_1 = loop_1.lineTo(0.99706, 0.70856)
loop_1 = loop_1.threePointArc((0.86844, 0.93153), (0.63217, 0.99839))
loop_1 = loop_1.lineTo(-0.6642, 1.0)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.5, 0.5)
loop_2 = loop_2.lineTo(0.52451, 0.49819)
loop_2 = loop_2.threePointArc((0.65526, 0.39302), (0.62462, 0.22289))
loop_2 = loop_2.lineTo(0.11714, -0.45162)
loop_2 = loop_2.threePointArc((-0.01844, -0.49873), (-0.14301, -0.419))
loop_2 = loop_2.lineTo(-0.64593, 0.253)
loop_2 = loop_2.threePointArc((-0.64497, 0.41495), (-0.50122, 0.49969))
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
