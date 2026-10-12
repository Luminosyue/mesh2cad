import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2467, 0.32966, 0.075), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.12966, 0.7533)
loop_1 = loop_1.lineTo(-0.47034, 0.7533)
loop_1 = loop_1.lineTo(-0.47034, -1.2467)
loop_1 = loop_1.lineTo(1.12966, -1.2467)
loop_1 = loop_1.lineTo(1.12966, 0.71758)
loop_1 = loop_1.lineTo(1.12966, 0.7533)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)
plane_2 = cq.Plane(origin=(0.08684, -0.02689, -0.075), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.77311, 1.08684)
loop_1 = loop_1.lineTo(0.82689, 1.08684)
loop_1 = loop_1.lineTo(0.82689, -0.91316)
loop_1 = loop_1.lineTo(-0.77311, -0.91316)
loop_1 = loop_1.lineTo(-0.77311, 1.05113)
loop_1 = loop_1.lineTo(-0.77311, 1.08684)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.15)

result = solid_1
result = result.add(solid_2)