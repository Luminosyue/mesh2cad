import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.2725), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.015, 0.55596)
loop_1 = loop_1.lineTo(-0.01242, -0.55596)
loop_1 = loop_1.lineTo(0.015, -0.55596)
loop_1 = loop_1.lineTo(0.01242, 0.55596)
loop_1 = loop_1.lineTo(-0.01424, 0.55596)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.55)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.275), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.015, 0.95)
loop_1 = loop_1.lineTo(-0.00978, -0.95)
loop_1 = loop_1.lineTo(0.015, -0.95)
loop_1 = loop_1.lineTo(0.00978, 0.95)
loop_1 = loop_1.lineTo(-0.0137, 0.95)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.55)

result = solid_1
result = result.add(solid_2)