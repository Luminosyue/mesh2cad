import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.61, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01215, 0.81036)
loop_1 = loop_1.lineTo(0.0184, 0.80033)
loop_1 = loop_1.threePointArc((0.02263, 0.76047), (0.02413, 0.71874))
loop_1 = loop_1.threePointArc((0.02693, 0.6027), (0.02521, 0.48295))
loop_1 = loop_1.threePointArc((0.02402, 0.05291), (0.02435, -0.35882))
loop_1 = loop_1.threePointArc((0.0232, -0.51196), (0.01901, -0.67032))
loop_1 = loop_1.lineTo(0.01125, -0.7908)
loop_1 = loop_1.threePointArc((0.00762, -0.80349), (2e-05, -0.81341))
loop_1 = loop_1.threePointArc((-0.01033, -0.81203), (-0.01402, -0.8071))
loop_1 = loop_1.threePointArc((-0.02098, -0.78023), (-0.0216, -0.75228))
loop_1 = loop_1.threePointArc((-0.02314, -0.72527), (-0.02308, -0.69829))
loop_1 = loop_1.threePointArc((-0.02121, -0.63318), (-0.02273, -0.57176))
loop_1 = loop_1.threePointArc((-0.01985, -0.05547), (-0.01477, 0.48121))
loop_1 = loop_1.lineTo(-0.00911, 0.7915)
loop_1 = loop_1.threePointArc((-0.00595, 0.80232), (-0.00203, 0.81177))
loop_1 = loop_1.lineTo(0.01215, 0.81036)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.59)

result = solid_1
