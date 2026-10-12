import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.81, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20329, 0.07688)
loop_1 = loop_1.lineTo(-0.27425, 0.07669)
loop_1 = loop_1.lineTo(-0.27406, 0.00591)
loop_1 = loop_1.lineTo(-0.20329, 0.0061)
loop_1 = loop_1.lineTo(-0.20329, 0.07679)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)
plane_2 = cq.Plane(origin=(-1.00011, -0.18073, 0.03556), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.09353, 0.07696)
loop_1 = loop_1.lineTo(0.09353, -0.04132)
loop_1 = loop_1.lineTo(-0.22483, -0.04132)
loop_1 = loop_1.lineTo(-0.22483, 0.07696)
loop_1 = loop_1.lineTo(0.08907, 0.07696)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.81)

result = solid_1
result = result.add(solid_2)