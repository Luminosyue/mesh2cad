import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00411, -0.00164, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18886, 0.00412)
loop_1 = loop_1.lineTo(-0.17436, -0.06879)
loop_1 = loop_1.lineTo(-0.13306, -0.13059)
loop_1 = loop_1.lineTo(-0.07126, -0.17188)
loop_1 = loop_1.lineTo(0.00164, -0.18639)
loop_1 = loop_1.lineTo(0.07454, -0.17188)
loop_1 = loop_1.lineTo(0.13635, -0.13059)
loop_1 = loop_1.lineTo(0.17764, -0.06879)
loop_1 = loop_1.lineTo(0.19214, 0.00411)
loop_1 = loop_1.lineTo(0.17764, 0.07701)
loop_1 = loop_1.lineTo(0.13635, 0.13882)
loop_1 = loop_1.lineTo(0.07454, 0.18011)
loop_1 = loop_1.lineTo(0.00164, 0.19461)
loop_1 = loop_1.lineTo(-0.07126, 0.18011)
loop_1 = loop_1.lineTo(-0.13306, 0.13882)
loop_1 = loop_1.lineTo(-0.17436, 0.07701)
loop_1 = loop_1.lineTo(-0.18768, 0.01004)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.00164, 0.00411)
loop_2 = loop_2.circle(0.12547)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
