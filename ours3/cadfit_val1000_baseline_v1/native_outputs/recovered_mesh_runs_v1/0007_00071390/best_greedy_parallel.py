import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14095, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.62857)
loop_1 = loop_1.lineTo(-0.33333, 0.62552)
loop_1 = loop_1.lineTo(-0.33232, 0.4381)
loop_1 = loop_1.lineTo(1.0, 0.44115)
loop_1 = loop_1.lineTo(1.0, 0.62755)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)
plane_2 = cq.Plane(origin=(-0.61905, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.33333, 0.34286)
loop_1 = loop_1.lineTo(0.33153, 0.08378)
loop_1 = loop_1.lineTo(-0.3373, -0.62857)
loop_1 = loop_1.lineTo(-0.57341, -0.62681)
loop_1 = loop_1.lineTo(-1.0, -0.24497)
loop_1 = loop_1.lineTo(-0.99735, 0.34286)
loop_1 = loop_1.lineTo(0.33201, 0.34286)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.95)

result = solid_1
result = result.add(solid_2)