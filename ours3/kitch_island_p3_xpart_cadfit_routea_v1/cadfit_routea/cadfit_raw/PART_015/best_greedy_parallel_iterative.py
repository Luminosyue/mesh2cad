import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0001, -0.00452, -0.00125), normal=(1.0, 0.00079, 0.00079), xDir=(0.00079, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04761, 0.02548)
loop_1 = loop_1.lineTo(-0.05792, 0.02043)
loop_1 = loop_1.lineTo(-0.0587, 0.00972)
loop_1 = loop_1.threePointArc((-0.05873, -6e-05), (-0.05882, -0.01025))
loop_1 = loop_1.threePointArc((-0.05824, -0.01643), (-0.0578, -0.02096))
loop_1 = loop_1.threePointArc((-0.05044, -0.0241), (-0.0459, -0.02542))
loop_1 = loop_1.threePointArc((-0.03636, -0.02539), (-0.02793, -0.02551))
loop_1 = loop_1.threePointArc((0.00114, -0.02564), (0.02738, -0.02566))
loop_1 = loop_1.threePointArc((0.03455, -0.02574), (0.0398, -0.02575))
loop_1 = loop_1.threePointArc((0.0458, -0.02386), (0.05051, -0.02238))
loop_1 = loop_1.threePointArc((0.05237, -0.01467), (0.05284, -0.01025))
loop_1 = loop_1.threePointArc((0.05282, 0.0011), (0.05286, 0.01117))
loop_1 = loop_1.threePointArc((0.05183, 0.01746), (0.0511, 0.02189))
loop_1 = loop_1.threePointArc((0.04441, 0.02437), (0.0398, 0.02579))
loop_1 = loop_1.threePointArc((0.02536, 0.02577), (0.01207, 0.02585))
loop_1 = loop_1.lineTo(-0.02155, 0.02588)
loop_1 = loop_1.threePointArc((-0.02981, 0.0259), (-0.0369, 0.02593))
loop_1 = loop_1.lineTo(-0.04761, 0.02548)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
