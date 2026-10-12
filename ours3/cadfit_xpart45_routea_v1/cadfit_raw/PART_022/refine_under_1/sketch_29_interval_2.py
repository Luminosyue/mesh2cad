import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.65172, -0.6778, -0.02073), normal=(-0.62608, -0.77892, -0.03614), xDir=(-0.77943, 0.62649, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08476, -0.15194)
loop_1 = loop_1.lineTo(0.11698, -0.17115)
loop_1 = loop_1.lineTo(0.09749, -0.18563)
loop_1 = loop_1.lineTo(0.08572, -0.18942)
loop_1 = loop_1.lineTo(0.07249, -0.18758)
loop_1 = loop_1.lineTo(0.04061, -0.17115)
loop_1 = loop_1.lineTo(0.07364, -0.14999)
loop_1 = loop_1.lineTo(0.08476, -0.15194)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_29_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_29_interval_2.stl')