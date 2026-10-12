import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01571, -0.79996, 0.00105), normal=(1e-05, 1.0, 0.00015), xDir=(1.0, -1e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.95073, 0.13295)
loop_1 = loop_1.lineTo(-1.01244, 0.13195)
loop_1 = loop_1.lineTo(-1.01553, 0.12154)
loop_1 = loop_1.lineTo(-1.01531, -0.12751)
loop_1 = loop_1.lineTo(-1.00133, -0.13044)
loop_1 = loop_1.lineTo(0.9826, -0.12859)
loop_1 = loop_1.lineTo(0.98397, 0.1265)
loop_1 = loop_1.lineTo(0.97357, 0.13284)
loop_1 = loop_1.lineTo(0.95302, 0.13289)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1
