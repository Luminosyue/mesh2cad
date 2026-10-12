import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.8, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.76, 1.0)
loop_1 = loop_1.lineTo(0.76, 0.99531)
loop_1 = loop_1.lineTo(0.75531, -1.0)
loop_1 = loop_1.lineTo(-0.76, -0.99531)
loop_1 = loop_1.lineTo(-0.76, 0.99765)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1
