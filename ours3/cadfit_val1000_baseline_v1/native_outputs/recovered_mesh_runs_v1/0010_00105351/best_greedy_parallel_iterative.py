import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00314, 1.0, -0.01397), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22223, 0.08549)
loop_1 = loop_1.lineTo(-0.21595, 0.08549)
loop_1 = loop_1.lineTo(-0.20778, 0.04293)
loop_1 = loop_1.lineTo(-0.19142, 0.0028)
loop_1 = loop_1.lineTo(-0.16752, -0.03334)
loop_1 = loop_1.lineTo(-0.13699, -0.0641)
loop_1 = loop_1.lineTo(-0.10103, -0.08828)
loop_1 = loop_1.lineTo(-0.06102, -0.10494)
loop_1 = loop_1.lineTo(-0.01853, -0.11344)
loop_1 = loop_1.lineTo(0.02481, -0.11344)
loop_1 = loop_1.lineTo(0.0673, -0.10494)
loop_1 = loop_1.lineTo(0.10731, -0.08828)
loop_1 = loop_1.lineTo(0.14327, -0.0641)
loop_1 = loop_1.lineTo(0.1738, -0.03334)
loop_1 = loop_1.lineTo(0.1977, 0.0028)
loop_1 = loop_1.lineTo(0.21406, 0.04293)
loop_1 = loop_1.lineTo(0.22123, 0.08031)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
