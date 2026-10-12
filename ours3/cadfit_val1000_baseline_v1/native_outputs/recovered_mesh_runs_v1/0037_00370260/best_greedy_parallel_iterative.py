import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00375, -0.01295, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56958, 0.23135)
loop_1 = loop_1.lineTo(-0.56958, -0.23886)
loop_1 = loop_1.lineTo(-0.29497, -0.51346)
loop_1 = loop_1.lineTo(0.32087, -0.51346)
loop_1 = loop_1.lineTo(0.59548, -0.23886)
loop_1 = loop_1.lineTo(0.59548, 0.23135)
loop_1 = loop_1.lineTo(0.32087, 0.50595)
loop_1 = loop_1.lineTo(-0.29497, 0.50595)
loop_1 = loop_1.lineTo(-0.56786, 0.23307)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
