import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.625, 0.625)
loop_1 = loop_1.lineTo(0.62333, 0.125)
loop_1 = loop_1.lineTo(-0.125, 0.12166)
loop_1 = loop_1.lineTo(-0.12833, -0.625)
loop_1 = loop_1.lineTo(-0.625, -0.62333)
loop_1 = loop_1.lineTo(-0.62166, 0.625)
loop_1 = loop_1.lineTo(0.62334, 0.625)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
