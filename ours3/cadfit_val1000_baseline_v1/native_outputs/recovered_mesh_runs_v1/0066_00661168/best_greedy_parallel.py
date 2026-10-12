import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.13323, 0.20165, -0.11369), normal=(0.0, -1.0, 0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24593, 0.88631)
loop_1 = loop_1.lineTo(0.36395, 0.08379)
loop_1 = loop_1.lineTo(0.72927, -0.49883)
loop_1 = loop_1.lineTo(0.12176, -0.10703)
loop_1 = loop_1.lineTo(-0.40892, -1.10563)
loop_1 = loop_1.lineTo(-0.20861, -0.00947)
loop_1 = loop_1.lineTo(-0.99378, 0.12463)
loop_1 = loop_1.lineTo(-0.12214, 0.26991)
loop_1 = loop_1.lineTo(0.24555, 0.88567)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1