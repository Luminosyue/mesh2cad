import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.44788), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28272, 1.0)
loop_1 = loop_1.lineTo(-0.2776, -1.0)
loop_1 = loop_1.lineTo(0.28272, -0.99829)
loop_1 = loop_1.lineTo(0.2776, 1.0)
loop_1 = loop_1.lineTo(-0.28101, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.89)
plane_2 = cq.Plane(origin=(0.0, -0.28728, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-1.0, 0.44212)
loop_1 = loop_1.lineTo(-0.99615, -0.44212)
loop_1 = loop_1.lineTo(1.0, -0.43827)
loop_1 = loop_1.lineTo(0.99615, 0.44212)
loop_1 = loop_1.lineTo(-0.99808, 0.44212)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.57)

result = solid_1
result = result.add(solid_2)