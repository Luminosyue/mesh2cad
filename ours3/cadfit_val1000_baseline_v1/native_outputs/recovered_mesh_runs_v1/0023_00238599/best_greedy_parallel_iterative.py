import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02065, -0.06048, 0.22317), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.74446, 1.22317)
loop_1 = loop_1.lineTo(-0.65399, 1.22317)
loop_1 = loop_1.lineTo(-0.65161, -0.68635)
loop_1 = loop_1.lineTo(0.61268, -0.68635)
loop_1 = loop_1.lineTo(0.61551, 1.22317)
loop_1 = loop_1.lineTo(0.70316, 1.22317)
loop_1 = loop_1.lineTo(0.70044, -0.77683)
loop_1 = loop_1.lineTo(-0.74446, -0.77683)
loop_1 = loop_1.lineTo(-0.74446, 1.214)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
