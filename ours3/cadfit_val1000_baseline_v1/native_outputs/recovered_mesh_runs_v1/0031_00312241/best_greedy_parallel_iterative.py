import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.44444, 0.31111)
loop_1 = loop_1.lineTo(-0.44304, -0.32929)
loop_1 = loop_1.threePointArc((-0.39098, -0.41769), (-0.29676, -0.44377))
loop_1 = loop_1.lineTo(0.32929, -0.44304)
loop_1 = loop_1.threePointArc((0.41769, -0.39098), (0.44377, -0.29676))
loop_1 = loop_1.lineTo(0.44304, 0.32929)
loop_1 = loop_1.threePointArc((0.39098, 0.41769), (0.29676, 0.44377))
loop_1 = loop_1.lineTo(-0.32929, 0.44304)
loop_1 = loop_1.threePointArc((-0.41279, 0.39718), (-0.44431, 0.31218))
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.35554, 0.26667)
loop_2 = loop_2.threePointArc((-0.32666, 0.33211), (-0.25595, 0.35501))
loop_2 = loop_2.lineTo(0.28055, 0.35434)
loop_2 = loop_2.threePointArc((0.33699, 0.32085), (0.35503, 0.25595))
loop_2 = loop_2.lineTo(0.35434, -0.28055)
loop_2 = loop_2.threePointArc((0.32086, -0.33699), (0.25595, -0.35503))
loop_2 = loop_2.lineTo(-0.28055, -0.35434)
loop_2 = loop_2.threePointArc((-0.33699, -0.32086), (-0.35503, -0.25595))
loop_2 = loop_2.lineTo(-0.35556, 0.26577)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
