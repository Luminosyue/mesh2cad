import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94092, -0.02345, 0.13133), normal=(-0.99993, -0.0005, 0.01148), xDir=(-0.0005, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18799, 0.65694)
loop_1 = loop_1.lineTo(0.14509, 0.67446)
loop_1 = loop_1.lineTo(0.10282, 0.68569)
loop_1 = loop_1.lineTo(0.04839, 0.69542)
loop_1 = loop_1.lineTo(0.02544, 0.69749)
loop_1 = loop_1.lineTo(0.41345, 0.69704)
loop_1 = loop_1.lineTo(0.41345, 0.14816)
loop_1 = loop_1.lineTo(0.02835, 0.14789)
loop_1 = loop_1.lineTo(-0.01093, 0.14585)
loop_1 = loop_1.lineTo(-0.06294, 0.14741)
loop_1 = loop_1.lineTo(0.19027, 0.59567)
loop_1 = loop_1.lineTo(0.20776, 0.64807)
loop_1 = loop_1.lineTo(0.18799, 0.65694)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_29_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_29_interval_1.stl')