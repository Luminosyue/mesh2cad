import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.08453, -0.38549, -0.08386), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82629, 0.37624)
loop_1 = loop_1.lineTo(1.08453, 0.37089)
loop_1 = loop_1.lineTo(1.0747, -0.10451)
loop_1 = loop_1.lineTo(-0.66257, -0.06856)
loop_1 = loop_1.lineTo(-0.6724, -0.54396)
loop_1 = loop_1.lineTo(-0.91547, -0.53878)
loop_1 = loop_1.lineTo(-0.91547, 0.19502)
loop_1 = loop_1.lineTo(0.82186, 0.16193)
loop_1 = loop_1.lineTo(0.82628, 0.37569)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.77)

result = solid_1
