import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.27007, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.96957, 0.51979)
loop_1 = loop_1.threePointArc((-0.97788, 0.49124), (-0.98387, 0.46745))
loop_1 = loop_1.lineTo(-0.99002, 0.40627)
loop_1 = loop_1.threePointArc((-0.99187, 0.36552), (-0.99274, 0.32655))
loop_1 = loop_1.threePointArc((-0.99279, 0.30428), (-0.99327, 0.28127))
loop_1 = loop_1.lineTo(-0.99275, 0.51982)
loop_1 = loop_1.lineTo(-0.9698, 0.51982)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_68_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_68_interval_0.stl')