import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.27294, 0.04235, 0.01687), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04241, -0.12711)
loop_1 = loop_1.circle(0.85406)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.25), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-7e-05, 0.02083)
loop_1 = loop_1.circle(0.72901)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.34)

result = solid_1
result = result.add(solid_2)