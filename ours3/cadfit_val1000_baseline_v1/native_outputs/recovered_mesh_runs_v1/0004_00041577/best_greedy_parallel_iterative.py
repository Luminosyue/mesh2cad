import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25577, 0.21906, -0.19118), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.76563, 0.74423)
loop_1 = loop_1.lineTo(0.76563, -1.25577)
loop_1 = loop_1.lineTo(-0.3275, -1.25577)
loop_1 = loop_1.lineTo(-0.3275, 0.74423)
loop_1 = loop_1.lineTo(0.73692, 0.74423)
loop_1 = loop_1.lineTo(0.76563, 0.74423)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.44368, 0.25011)
loop_2 = loop_2.lineTo(0.06728, 0.25011)
loop_2 = loop_2.lineTo(0.06728, -0.83439)
loop_2 = loop_2.lineTo(0.44368, -0.83439)
loop_2 = loop_2.lineTo(0.44368, -0.27847)
loop_2 = loop_2.lineTo(0.25633, -0.27847)
loop_2 = loop_2.lineTo(0.25633, 0.04789)
loop_2 = loop_2.lineTo(0.44368, 0.04789)
loop_2 = loop_2.lineTo(0.44368, 0.23414)
loop_2 = loop_2.lineTo(0.44368, 0.25011)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
