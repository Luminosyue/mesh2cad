import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.86, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.20875, 0.37037)
loop_1 = loop_1.lineTo(-0.20875, 0.36883)
loop_1 = loop_1.lineTo(-0.20721, -0.10774)
loop_1 = loop_1.lineTo(-0.16364, -0.10774)
loop_1 = loop_1.lineTo(-0.16286, -0.37037)
loop_1 = loop_1.lineTo(0.17441, -0.36883)
loop_1 = loop_1.lineTo(0.17517, -0.10774)
loop_1 = loop_1.lineTo(0.20875, -0.10774)
loop_1 = loop_1.lineTo(0.20875, 0.3696)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.72)

result = solid_1
