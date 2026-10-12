import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03704, 1.0)
loop_1 = loop_1.lineTo(0.03233, -0.70371)
loop_1 = loop_1.lineTo(-0.03704, -0.70252)
loop_1 = loop_1.lineTo(-0.03233, 1.0)
loop_1 = loop_1.lineTo(0.03586, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)
plane_2 = cq.Plane(origin=(0.0, -0.03704, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-1.0, 1.0)
loop_1 = loop_1.lineTo(1.0, 0.99478)
loop_1 = loop_1.lineTo(0.99446, -0.70926)
loop_1 = loop_1.lineTo(0.70201, -1.0)
loop_1 = loop_1.lineTo(-1.0, -0.99478)
loop_1 = loop_1.lineTo(-1.0, 0.99739)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.07)

result = solid_1
result = result.add(solid_2)