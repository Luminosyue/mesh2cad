import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01469, -0.43143, -0.11844), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98531, 0.59585)
loop_1 = loop_1.lineTo(-0.98531, -0.2613)
loop_1 = loop_1.lineTo(-0.41389, -0.2613)
loop_1 = loop_1.lineTo(-0.41389, -0.83273)
loop_1 = loop_1.lineTo(0.44326, -0.83273)
loop_1 = loop_1.lineTo(0.44326, -0.2613)
loop_1 = loop_1.lineTo(1.01469, -0.2613)
loop_1 = loop_1.lineTo(1.01469, 0.59585)
loop_1 = loop_1.lineTo(-0.97698, 0.59585)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.86)

result = solid_1
