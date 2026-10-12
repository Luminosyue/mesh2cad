import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.31628, 0.07988, 0.10889), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.74655, 0.68372)
loop_1 = loop_1.lineTo(0.74655, -0.64962)
loop_1 = loop_1.lineTo(0.41321, -0.64962)
loop_1 = loop_1.lineTo(0.41321, -1.31628)
loop_1 = loop_1.lineTo(-0.25345, -1.31628)
loop_1 = loop_1.lineTo(-0.25345, -0.64962)
loop_1 = loop_1.lineTo(-0.58679, -0.64962)
loop_1 = loop_1.lineTo(-0.58679, 0.68372)
loop_1 = loop_1.lineTo(0.71321, 0.68372)
loop_1 = loop_1.lineTo(0.74655, 0.68372)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.45345, 0.55039)
loop_2 = loop_2.circle(0.08867)
loop_3 = sketch_1.moveTo(-0.45345, -0.51628)
loop_3 = loop_3.circle(0.08867)
loop_4 = sketch_1.moveTo(0.61321, 0.55039)
loop_4 = loop_4.circle(0.08867)
loop_5 = sketch_1.moveTo(0.61321, -0.51628)
loop_5 = loop_5.circle(0.08867)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3).add(loop_4).add(loop_5)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
