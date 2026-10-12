import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00442, 1.0, -0.08938), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.00442, 0.57729)
loop_1 = loop_1.lineTo(-0.99558, 0.57729)
loop_1 = loop_1.lineTo(-0.99558, -0.75604)
loop_1 = loop_1.lineTo(-0.49558, -0.75396)
loop_1 = loop_1.lineTo(-0.49558, -0.42271)
loop_1 = loop_1.lineTo(0.50442, -0.42479)
loop_1 = loop_1.lineTo(0.50442, -0.75604)
loop_1 = loop_1.lineTo(1.00442, -0.75604)
loop_1 = loop_1.lineTo(1.00442, 0.56896)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
