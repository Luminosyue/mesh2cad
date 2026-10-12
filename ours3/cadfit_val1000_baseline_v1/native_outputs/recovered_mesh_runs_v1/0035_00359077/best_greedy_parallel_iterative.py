import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.72016, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16067, -0.16916)
loop_1 = loop_1.lineTo(0.16181, -0.00025)
loop_1 = loop_1.lineTo(0.86576, 0.00211)
loop_1 = loop_1.lineTo(0.86573, 0.25)
loop_1 = loop_1.lineTo(-0.86576, 0.24581)
loop_1 = loop_1.lineTo(-0.86573, 0.0)
loop_1 = loop_1.lineTo(-0.86462, 0.24975)
loop_1 = loop_1.lineTo(0.86576, 0.24785)
loop_1 = loop_1.lineTo(0.86462, 0.00025)
loop_1 = loop_1.lineTo(0.13653, -0.00174)
loop_1 = loop_1.lineTo(0.16067, -0.16914)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.41)

result = solid_1