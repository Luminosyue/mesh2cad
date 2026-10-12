import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.33994, -0.4292, 0.1666), normal=(1.0, 0.00016, -0.00068), xDir=(0.00016, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11642, 0.5913)
loop_1 = loop_1.threePointArc((-0.11664, 0.38308), (-0.11733, 0.16618))
loop_1 = loop_1.lineTo(-0.09694, 0.16618)
loop_1 = loop_1.lineTo(0.50866, 0.16618)
loop_1 = loop_1.lineTo(0.50866, -0.25893)
loop_1 = loop_1.lineTo(-0.42917, -0.25893)
loop_1 = loop_1.lineTo(-0.42917, 0.16618)
loop_1 = loop_1.lineTo(-0.74137, 0.16618)
loop_1 = loop_1.lineTo(-0.74141, 0.18773)
loop_1 = loop_1.threePointArc((-0.74186, 0.3854), (-0.74224, 0.5913))
loop_1 = loop_1.lineTo(-0.11779, 0.5913)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.63)
plane_2 = cq.Plane(origin=(-0.23719, -0.00467, 0.00489), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.00474, -0.23719)
loop_1 = loop_1.circle(0.99988)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.43)

result = solid_1
result = result.add(solid_2)