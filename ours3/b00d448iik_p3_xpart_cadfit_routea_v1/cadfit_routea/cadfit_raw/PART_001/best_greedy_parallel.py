import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.10315), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02595, -0.23305)
loop_1 = loop_1.lineTo(-0.02262, -0.99469)
loop_1 = loop_1.threePointArc((0.00116, -0.99983), (0.0199, -0.99856))
loop_1 = loop_1.lineTo(0.02165, 0.99741)
loop_1 = loop_1.threePointArc((0.00815, 0.99973), (-0.00407, 0.99895))
loop_1 = loop_1.threePointArc((-0.01434, 0.99886), (-0.02191, 0.99501))
loop_1 = loop_1.lineTo(-0.02594, -0.23176)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.10685), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.0262, 0.03862)
loop_1 = loop_1.lineTo(-0.02247, -0.99534)
loop_1 = loop_1.threePointArc((0.00147, -1.00014), (0.02083, -0.99845))
loop_1 = loop_1.lineTo(0.02212, 0.99746)
loop_1 = loop_1.threePointArc((-7e-05, 0.99994), (-0.01554, 0.99906))
loop_1 = loop_1.lineTo(-0.02619, 0.04033)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.22)

result = solid_1
result = result.add(solid_2)