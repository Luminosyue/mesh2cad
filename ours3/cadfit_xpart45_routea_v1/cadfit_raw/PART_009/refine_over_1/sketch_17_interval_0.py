import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.91812, -0.32318, 0.00881), normal=(0.9762, 0.21686, 0.00033), xDir=(0.21686, -0.9762, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26237, -0.07324)
loop_1 = loop_1.lineTo(-0.27381, -0.07301)
loop_1 = loop_1.lineTo(-0.30172, -0.08142)
loop_1 = loop_1.lineTo(-0.3146, -0.08336)
loop_1 = loop_1.lineTo(-0.33665, -0.08453)
loop_1 = loop_1.lineTo(-0.36786, -0.09366)
loop_1 = loop_1.lineTo(-0.37687, -0.11037)
loop_1 = loop_1.lineTo(-0.37805, 0.13187)
loop_1 = loop_1.lineTo(-0.36784, 0.11739)
loop_1 = loop_1.lineTo(-0.31459, 0.09044)
loop_1 = loop_1.lineTo(-0.28613, 0.08237)
loop_1 = loop_1.lineTo(-0.25718, -0.06907)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_17_interval_0.stl')