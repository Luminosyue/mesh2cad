import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.10845, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.1553)
loop_1 = loop_1.lineTo(-0.86351, 0.15124)
loop_1 = loop_1.lineTo(-0.99898, 0.02107)
loop_1 = loop_1.lineTo(-0.86705, -0.11536)
loop_1 = loop_1.lineTo(1.0, -0.15089)
loop_1 = loop_1.lineTo(1.0, 0.15383)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
