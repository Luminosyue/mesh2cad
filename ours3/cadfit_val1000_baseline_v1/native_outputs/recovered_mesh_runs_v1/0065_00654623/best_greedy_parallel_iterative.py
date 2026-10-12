import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.83, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95277, 0.8341)
loop_1 = loop_1.lineTo(0.00631, 0.83059)
loop_1 = loop_1.lineTo(0.00281, -0.11916)
loop_1 = loop_1.lineTo(-0.22262, -0.12091)
loop_1 = loop_1.lineTo(-0.22612, -0.8341)
loop_1 = loop_1.lineTo(-0.45942, -0.83235)
loop_1 = loop_1.lineTo(-0.46119, -0.11916)
loop_1 = loop_1.lineTo(-0.95277, -0.1174)
loop_1 = loop_1.lineTo(-0.95277, 0.83235)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.91)

result = solid_1
