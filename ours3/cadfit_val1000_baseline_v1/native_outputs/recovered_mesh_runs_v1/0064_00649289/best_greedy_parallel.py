import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.09998, 0.21891, 0.06828), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06065, -0.30903)
loop_1 = loop_1.lineTo(-0.09664, 0.32298)
loop_1 = loop_1.threePointArc((0.01896, 0.02319), (0.0605, -0.30139))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)
plane_2 = cq.Plane(origin=(-0.31444, -0.00261, -0.00787), normal=(0.99887, -0.04749, -0.0), xDir=(-0.04749, -0.99887, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.28614, 0.06385)
loop_1 = loop_1.lineTo(-0.30548, 0.06385)
loop_1 = loop_1.lineTo(-0.30548, -0.07959)
loop_1 = loop_1.lineTo(-0.28614, -0.07959)
loop_1 = loop_1.lineTo(-0.28614, 0.06222)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.34)

result = solid_1
result = result.add(solid_2)