import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07919, 0.38264)
loop_1 = loop_1.lineTo(-0.0625, 0.36901)
loop_1 = loop_1.threePointArc((-0.05454, 0.36575), (-0.04683, 0.36281))
loop_1 = loop_1.lineTo(-0.00261, 0.37597)
loop_1 = loop_1.lineTo(0.00544, 0.39335)
loop_1 = loop_1.threePointArc((0.00577, 0.40044), (0.00624, 0.40782))
loop_1 = loop_1.lineTo(0.00299, 0.42047)
loop_1 = loop_1.threePointArc((-0.00645, 0.43456), (-0.0108, 0.44044))
loop_1 = loop_1.lineTo(-0.0317, 0.45021)
loop_1 = loop_1.threePointArc((-0.03934, 0.45138), (-0.04667, 0.45246))
loop_1 = loop_1.threePointArc((-0.05507, 0.44992), (-0.06227, 0.44777))
loop_1 = loop_1.lineTo(-0.07353, 0.3849)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_21_interval_0.stl')