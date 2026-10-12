import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07562, -0.19062)
loop_1 = loop_1.lineTo(-0.05446, -0.23033)
loop_1 = loop_1.threePointArc((-0.02445, -0.23705), (-0.00273, -0.2383))
loop_1 = loop_1.lineTo(0.03139, -0.23835)
loop_1 = loop_1.lineTo(0.04859, -0.22929)
loop_1 = loop_1.lineTo(0.07043, -0.20336)
loop_1 = loop_1.lineTo(0.07593, -0.19023)
loop_1 = loop_1.threePointArc((0.07498, -0.14339), (0.0752, -0.095))
loop_1 = loop_1.threePointArc((0.07519, -0.04245), (0.07478, 0.00763))
loop_1 = loop_1.threePointArc((0.07513, 0.05323), (0.07472, 0.09664))
loop_1 = loop_1.lineTo(0.07489, 0.20267)
loop_1 = loop_1.lineTo(0.02992, 0.23898)
loop_1 = loop_1.threePointArc((-0.0102, 0.23824), (-0.04833, 0.2368))
loop_1 = loop_1.lineTo(-0.0754, 0.2016)
loop_1 = loop_1.threePointArc((-0.07518, 0.15932), (-0.07545, 0.11569))
loop_1 = loop_1.lineTo(-0.07557, -0.18401)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
