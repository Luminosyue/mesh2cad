import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14159, 0.27861)
loop_1 = loop_1.lineTo(0.13988, -0.55635)
loop_1 = loop_1.threePointArc((-0.13725, -0.62383), (-0.42506, -0.55514))
loop_1 = loop_1.lineTo(-0.42289, 0.27861)
loop_1 = loop_1.lineTo(0.14065, 0.27861)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
