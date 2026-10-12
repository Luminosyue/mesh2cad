import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.67657, 0.00901, -0.01485), normal=(1.0, -0.00074, 0.00107), xDir=(-0.00074, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19352, -0.18712)
loop_1 = loop_1.lineTo(0.19295, -0.13708)
loop_1 = loop_1.lineTo(0.22516, -0.08982)
loop_1 = loop_1.lineTo(0.22678, -0.23814)
loop_1 = loop_1.lineTo(0.22237, -0.22097)
loop_1 = loop_1.lineTo(0.2143, -0.20935)
loop_1 = loop_1.lineTo(0.19352, -0.18712)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_6_interval_1.stl')