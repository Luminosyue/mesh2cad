import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98918, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01519, -0.41738)
loop_1 = loop_1.threePointArc((0.00757, -0.41726), (-0.00036, -0.41679))
loop_1 = loop_1.lineTo(-0.03825, -0.4154)
loop_1 = loop_1.threePointArc((-0.05513, -0.41506), (-0.07247, -0.41434))
loop_1 = loop_1.lineTo(-0.09444, -0.41382)
loop_1 = loop_1.threePointArc((-0.10257, -0.41369), (-0.1108, -0.41321))
loop_1 = loop_1.lineTo(-0.14606, -0.41191)
loop_1 = loop_1.threePointArc((-0.15314, -0.41188), (-0.16027, -0.41145))
loop_1 = loop_1.lineTo(-0.19789, -0.41007)
loop_1 = loop_1.lineTo(-0.27044, -0.40157)
loop_1 = loop_1.lineTo(-0.30293, -0.39707)
loop_1 = loop_1.lineTo(0.01498, -0.41736)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_72_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_72_interval_0.stl')