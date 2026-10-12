import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00801, -1.0, 0.03823), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14199, 0.53823)
loop_1 = loop_1.lineTo(-0.14199, 0.33823)
loop_1 = loop_1.lineTo(-0.29199, 0.33823)
loop_1 = loop_1.lineTo(-0.29199, -0.46177)
loop_1 = loop_1.lineTo(0.30801, -0.46177)
loop_1 = loop_1.lineTo(0.30801, 0.33823)
loop_1 = loop_1.lineTo(0.15801, 0.33823)
loop_1 = loop_1.lineTo(0.15801, 0.53823)
loop_1 = loop_1.lineTo(-0.12574, 0.53823)
loop_1 = loop_1.lineTo(-0.14199, 0.53823)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.00801, -0.06177)
loop_2 = loop_2.circle(0.14819)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
