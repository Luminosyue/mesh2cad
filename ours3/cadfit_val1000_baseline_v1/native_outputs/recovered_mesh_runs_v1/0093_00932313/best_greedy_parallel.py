import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.48, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.04)
loop_1 = loop_1.lineTo(-1.0, 0.03448)
loop_1 = loop_1.lineTo(-0.99861, -0.04)
loop_1 = loop_1.lineTo(1.0, -0.03448)
loop_1 = loop_1.lineTo(1.0, 0.03862)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.96)
plane_2 = cq.Plane(origin=(-0.48, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(1.0, 0.04)
loop_1 = loop_1.lineTo(0.99861, -0.04)
loop_1 = loop_1.lineTo(-1.0, -0.03442)
loop_1 = loop_1.lineTo(-0.99861, 0.04)
loop_1 = loop_1.lineTo(0.99861, 0.04)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.96)

result = solid_1
result = result.add(solid_2)