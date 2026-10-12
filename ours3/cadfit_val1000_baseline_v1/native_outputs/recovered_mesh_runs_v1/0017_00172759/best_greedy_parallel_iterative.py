import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0875, 0.0875)
loop_1 = loop_1.lineTo(0.08703, -0.0875)
loop_1 = loop_1.lineTo(-0.0875, -0.08703)
loop_1 = loop_1.lineTo(-0.08703, 0.0875)
loop_1 = loop_1.lineTo(0.08727, 0.0875)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.0375, 0.0375)
loop_2 = loop_2.lineTo(-0.0375, 0.0373)
loop_2 = loop_2.lineTo(-0.0373, -0.0375)
loop_2 = loop_2.lineTo(0.0375, -0.0373)
loop_2 = loop_2.lineTo(0.0375, 0.0374)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
