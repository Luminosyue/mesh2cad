import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8, 0.00843, -0.09736), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80843, 0.90264)
loop_1 = loop_1.lineTo(0.80843, -1.09736)
loop_1 = loop_1.lineTo(0.40843, -1.09736)
loop_1 = loop_1.lineTo(0.40843, -0.738)
loop_1 = loop_1.lineTo(-0.39157, -0.738)
loop_1 = loop_1.lineTo(-0.39157, -1.09736)
loop_1 = loop_1.lineTo(-0.79157, -1.09736)
loop_1 = loop_1.lineTo(-0.79157, 0.90264)
loop_1 = loop_1.lineTo(0.79593, 0.90264)
loop_1 = loop_1.lineTo(0.80843, 0.90264)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1
