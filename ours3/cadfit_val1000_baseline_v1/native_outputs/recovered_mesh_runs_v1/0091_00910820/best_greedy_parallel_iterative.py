import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.28047), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99935, -0.00291)
loop_1 = loop_1.lineTo(-0.02791, -0.00082)
loop_1 = loop_1.lineTo(-0.99935, 0.00291)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.56)
plane_2 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.00291, 0.27869)
loop_1 = loop_1.lineTo(0.00136, -0.27907)
loop_1 = loop_1.lineTo(-0.00291, 0.27869)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)