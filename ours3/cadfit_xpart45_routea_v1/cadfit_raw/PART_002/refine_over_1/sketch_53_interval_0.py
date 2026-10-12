import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03231, 0.39762, 0.16453), normal=(0.00036, -0.99292, -0.11878), xDir=(-1.0, -0.00036, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21523, -0.25633)
loop_1 = loop_1.lineTo(-0.20067, -0.26759)
loop_1 = loop_1.lineTo(-0.18112, -0.28528)
loop_1 = loop_1.lineTo(-0.15701, -0.29819)
loop_1 = loop_1.lineTo(-0.14411, -0.30784)
loop_1 = loop_1.lineTo(-0.11809, -0.3242)
loop_1 = loop_1.lineTo(-0.10402, -0.33281)
loop_1 = loop_1.threePointArc((-0.08671, -0.34001), (-0.07007, -0.34688))
loop_1 = loop_1.lineTo(-0.04101, -0.35529)
loop_1 = loop_1.lineTo(-0.02968, -0.35735)
loop_1 = loop_1.threePointArc((-0.01252, -0.35748), (0.00396, -0.35748))
loop_1 = loop_1.threePointArc((0.02119, -0.36046), (0.03461, -0.36273))
loop_1 = loop_1.lineTo(-0.22741, -0.36306)
loop_1 = loop_1.lineTo(-0.22742, -0.24508)
loop_1 = loop_1.lineTo(-0.21523, -0.25633)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_53_interval_0.stl')