import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.21973, 0.246, -0.0488), normal=(0.0, -1.0, 0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78027, 0.0512)
loop_1 = loop_1.lineTo(-1.21973, 0.0512)
loop_1 = loop_1.lineTo(-1.21973, -0.0488)
loop_1 = loop_1.lineTo(-1.16973, -0.0488)
loop_1 = loop_1.lineTo(-1.16973, -0.1488)
loop_1 = loop_1.lineTo(-1.12973, -0.1488)
loop_1 = loop_1.lineTo(-1.12973, -0.0488)
loop_1 = loop_1.lineTo(-0.75973, -0.0488)
loop_1 = loop_1.lineTo(-0.75973, -0.1488)
loop_1 = loop_1.lineTo(-0.71973, -0.1488)
loop_1 = loop_1.lineTo(-0.71973, -0.0488)
loop_1 = loop_1.lineTo(0.78027, -0.0488)
loop_1 = loop_1.lineTo(0.78027, 0.0272)
loop_1 = loop_1.lineTo(0.78027, 0.0512)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.49)

result = solid_1
