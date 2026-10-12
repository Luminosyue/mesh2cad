import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66667, 0.83333)
loop_1 = loop_1.lineTo(-0.66658, 0.82891)
loop_1 = loop_1.lineTo(-0.62794, -0.83333)
loop_1 = loop_1.lineTo(-0.29903, -0.83113)
loop_1 = loop_1.lineTo(-0.29682, -0.5)
loop_1 = loop_1.lineTo(0.36764, -0.50221)
loop_1 = loop_1.lineTo(0.36986, -0.83333)
loop_1 = loop_1.lineTo(0.66667, -0.83112)
loop_1 = loop_1.lineTo(0.66667, 0.83112)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
