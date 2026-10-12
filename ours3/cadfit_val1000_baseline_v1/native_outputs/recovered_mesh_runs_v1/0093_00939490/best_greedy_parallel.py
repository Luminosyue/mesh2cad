import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.08491, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.04717)
loop_1 = loop_1.lineTo(-1.0, 0.04162)
loop_1 = loop_1.lineTo(-0.9986, -0.04717)
loop_1 = loop_1.lineTo(1.0, -0.04162)
loop_1 = loop_1.lineTo(1.0, 0.04578)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1