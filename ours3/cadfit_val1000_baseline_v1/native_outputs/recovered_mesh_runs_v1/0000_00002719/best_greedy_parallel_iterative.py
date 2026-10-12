import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.10085, 0.20259, 1.0), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.73259, 0.56915)
loop_1 = loop_1.lineTo(0.73259, 0.38915)
loop_1 = loop_1.lineTo(-0.14741, 0.38915)
loop_1 = loop_1.lineTo(-0.14741, -0.59085)
loop_1 = loop_1.lineTo(0.73259, -0.59197)
loop_1 = loop_1.lineTo(0.73259, -0.77085)
loop_1 = loop_1.lineTo(-0.32741, -0.77085)
loop_1 = loop_1.lineTo(-0.32741, 0.56915)
loop_1 = loop_1.lineTo(0.72762, 0.56915)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
