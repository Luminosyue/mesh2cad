import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.26656, -0.08622, -0.51619), normal=(0.01029, -0.00035, 0.99995), xDir=(-0.0, 1.0, 0.00035))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.95939, -0.68618)
loop_1 = loop_1.threePointArc((0.98551, -0.63688), (1.01044, -0.58947))
loop_1 = loop_1.lineTo(1.02175, -0.55707)
loop_1 = loop_1.lineTo(1.03103, -0.52585)
loop_1 = loop_1.lineTo(1.03902, -0.49337)
loop_1 = loop_1.lineTo(1.04575, -0.45852)
loop_1 = loop_1.lineTo(1.05077, -0.42508)
loop_1 = loop_1.lineTo(1.0586, -0.3842)
loop_1 = loop_1.lineTo(1.05017, -0.40133)
loop_1 = loop_1.threePointArc((1.04563, -0.42735), (1.0414, -0.45236))
loop_1 = loop_1.threePointArc((1.03397, -0.48306), (1.0268, -0.51158))
loop_1 = loop_1.lineTo(1.01553, -0.54839)
loop_1 = loop_1.lineTo(1.00732, -0.57785)
loop_1 = loop_1.lineTo(1.00137, -0.59031)
loop_1 = loop_1.lineTo(0.99709, -0.6062)
loop_1 = loop_1.lineTo(0.97618, -0.65199)
loop_1 = loop_1.lineTo(0.96091, -0.68307)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.62)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_7_interval_0.stl')