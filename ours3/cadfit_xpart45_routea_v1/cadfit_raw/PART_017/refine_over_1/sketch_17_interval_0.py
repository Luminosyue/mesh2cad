import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00681, -1.02326, 0.48031), normal=(0.0008, 0.92144, 0.38851), xDir=(1.0, -0.00087, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00159, 1.52177)
loop_1 = loop_1.lineTo(-0.32439, 1.52147)
loop_1 = loop_1.lineTo(-0.3242, 1.45181)
loop_1 = loop_1.lineTo(-0.28482, 1.46426)
loop_1 = loop_1.lineTo(-0.24618, 1.47721)
loop_1 = loop_1.threePointArc((-0.22509, 1.4828), (-0.20756, 1.48775))
loop_1 = loop_1.lineTo(-0.16121, 1.49921)
loop_1 = loop_1.threePointArc((-0.1441, 1.50314), (-0.13027, 1.50625))
loop_1 = loop_1.threePointArc((-0.1097, 1.50988), (-0.09164, 1.51281))
loop_1 = loop_1.threePointArc((-0.07009, 1.51527), (-0.05301, 1.51738))
loop_1 = loop_1.threePointArc((-0.03141, 1.51916), (-0.01437, 1.52086))
loop_1 = loop_1.lineTo(0.00018, 1.5217)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_17_interval_0.stl')