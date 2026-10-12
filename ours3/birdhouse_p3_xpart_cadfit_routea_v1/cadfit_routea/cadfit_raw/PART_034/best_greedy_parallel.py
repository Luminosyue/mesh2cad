import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.98, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02825, 0.13777)
loop_1 = loop_1.lineTo(0.04314, 0.13751)
loop_1 = loop_1.lineTo(0.04788, 0.11954)
loop_1 = loop_1.threePointArc((0.02941, 0.11706), (0.01581, 0.11723))
loop_1 = loop_1.threePointArc((0.00747, 0.1173), (-0.00103, 0.11763))
loop_1 = loop_1.lineTo(-0.01466, 0.10489)
loop_1 = loop_1.lineTo(-0.01447, 0.01903)
loop_1 = loop_1.lineTo(-0.01377, -0.01296)
loop_1 = loop_1.lineTo(-0.01289, -0.04176)
loop_1 = loop_1.lineTo(-0.01473, -0.05538)
loop_1 = loop_1.lineTo(-0.0302, -0.05871)
loop_1 = loop_1.lineTo(-0.03854, -0.04016)
loop_1 = loop_1.threePointArc((-0.03836, -0.0057), (-0.0387, 0.02721))
loop_1 = loop_1.threePointArc((-0.03864, 0.06004), (-0.03845, 0.09404))
loop_1 = loop_1.threePointArc((-0.03873, 0.10727), (-0.03915, 0.11979))
loop_1 = loop_1.threePointArc((-0.03509, 0.12726), (-0.03154, 0.13434))
loop_1 = loop_1.threePointArc((-0.01387, 0.13655), (0.00265, 0.13756))
loop_1 = loop_1.threePointArc((0.01519, 0.13766), (0.02807, 0.13778))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.81)

result = solid_1