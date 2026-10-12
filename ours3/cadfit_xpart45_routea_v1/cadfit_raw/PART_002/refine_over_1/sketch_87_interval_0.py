import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.7708), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25881, 0.32894)
loop_1 = loop_1.lineTo(0.26775, 0.30993)
loop_1 = loop_1.lineTo(0.2792, 0.28287)
loop_1 = loop_1.threePointArc((0.28738, 0.26313), (0.29564, 0.24454))
loop_1 = loop_1.threePointArc((0.299, 0.23695), (0.30262, 0.23005))
loop_1 = loop_1.threePointArc((0.31037, 0.21052), (0.31788, 0.19016))
loop_1 = loop_1.threePointArc((0.32387, 0.17109), (0.32993, 0.15135))
loop_1 = loop_1.lineTo(0.3377, 0.12337)
loop_1 = loop_1.lineTo(0.34783, 0.08227)
loop_1 = loop_1.threePointArc((0.34609, 0.09829), (0.34418, 0.11348))
loop_1 = loop_1.lineTo(0.34021, 0.13768)
loop_1 = loop_1.lineTo(0.33147, 0.17627)
loop_1 = loop_1.lineTo(0.3215, 0.21313)
loop_1 = loop_1.lineTo(0.31061, 0.24761)
loop_1 = loop_1.threePointArc((0.29805, 0.27411), (0.28319, 0.29783))
loop_1 = loop_1.threePointArc((0.27184, 0.31456), (0.25891, 0.3288))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_87_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_87_interval_0.stl')