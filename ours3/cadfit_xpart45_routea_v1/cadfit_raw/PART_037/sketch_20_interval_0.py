import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45951, 0.08656, 0.27458), normal=(-0.00174, 0.42485, -0.90526), xDir=(0.0, -0.90526, -0.42485))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28409, 0.00234)
loop_1 = loop_1.threePointArc((0.27556, -0.01357), (0.26945, -0.02007))
loop_1 = loop_1.lineTo(0.23791, -0.03199)
loop_1 = loop_1.threePointArc((0.23118, -0.02992), (0.22425, -0.02752))
loop_1 = loop_1.lineTo(0.19352, -0.00731)
loop_1 = loop_1.lineTo(0.18122, 0.02421)
loop_1 = loop_1.lineTo(0.18853, 0.03617)
loop_1 = loop_1.lineTo(0.22991, 0.05658)
loop_1 = loop_1.lineTo(0.24078, 0.0575)
loop_1 = loop_1.threePointArc((0.24642, 0.05724), (0.25184, 0.05699))
loop_1 = loop_1.threePointArc((0.26193, 0.05117), (0.26802, 0.04726))
loop_1 = loop_1.lineTo(0.27915, 0.03162)
loop_1 = loop_1.lineTo(0.28346, 0.01983)
loop_1 = loop_1.threePointArc((0.28422, 0.01345), (0.28478, 0.00818))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_20_interval_0.stl')