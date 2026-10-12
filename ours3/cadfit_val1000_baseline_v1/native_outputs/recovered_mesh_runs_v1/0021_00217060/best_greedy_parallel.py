import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.83231, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.61538, 1.0)
loop_1 = loop_1.lineTo(0.61538, 0.84615)
loop_1 = loop_1.lineTo(0.46154, 0.84615)
loop_1 = loop_1.lineTo(0.45722, -1.0)
loop_1 = loop_1.lineTo(-0.61538, -0.99569)
loop_1 = loop_1.lineTo(-0.61108, 1.0)
loop_1 = loop_1.lineTo(0.61323, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.82)

result = solid_1