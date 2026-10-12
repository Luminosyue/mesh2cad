import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.98, 0.53041, 0.00575), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.43575, 0.06457)
loop_1 = loop_1.lineTo(-0.43482, -0.05308)
loop_1 = loop_1.lineTo(0.39606, -0.05234)
loop_1 = loop_1.lineTo(0.39606, 0.06457)
loop_1 = loop_1.lineTo(-0.43482, 0.06457)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)
plane_2 = cq.Plane(origin=(-0.98, 0.5709, -4e-05), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.47624, 0.05878)
loop_1 = loop_1.lineTo(0.47554, -0.05887)
loop_1 = loop_1.lineTo(-0.35558, -0.05777)
loop_1 = loop_1.lineTo(-0.35558, 0.05878)
loop_1 = loop_1.lineTo(0.47554, 0.05878)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.96)

result = solid_1
result = result.add(solid_2)