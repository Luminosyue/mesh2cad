import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.1879, 0.66793)
loop_1 = loop_1.lineTo(0.18654, 0.02788)
loop_1 = loop_1.lineTo(-0.1879, 0.02924)
loop_1 = loop_1.lineTo(-0.18654, 0.66793)
loop_1 = loop_1.lineTo(0.18722, 0.66793)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.43)
plane_2 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.1879, 0.66793)
loop_1 = loop_1.lineTo(0.18654, 0.02788)
loop_1 = loop_1.lineTo(-0.1879, 0.02924)
loop_1 = loop_1.lineTo(-0.18654, 0.66793)
loop_1 = loop_1.lineTo(0.18722, 0.66793)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.43)

result = solid_1
result = result.add(solid_2)