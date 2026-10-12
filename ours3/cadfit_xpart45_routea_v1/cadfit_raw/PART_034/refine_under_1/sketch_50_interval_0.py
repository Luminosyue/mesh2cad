import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.62491, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95064, -0.26933)
loop_1 = loop_1.lineTo(0.94154, -0.29164)
loop_1 = loop_1.lineTo(0.88632, -0.31018)
loop_1 = loop_1.threePointArc((0.82867, -0.32), (0.7694, -0.32588))
loop_1 = loop_1.threePointArc((0.73418, -0.32625), (0.69892, -0.3239))
loop_1 = loop_1.lineTo(0.46421, -0.32041)
loop_1 = loop_1.threePointArc((0.31246, -0.3226), (0.15571, -0.32347))
loop_1 = loop_1.lineTo(-0.01653, -0.32022)
loop_1 = loop_1.threePointArc((-0.14463, -0.31816), (-0.2664, -0.31816))
loop_1 = loop_1.threePointArc((-0.44529, -0.31559), (-0.63014, -0.30771))
loop_1 = loop_1.lineTo(-0.68169, -0.31103)
loop_1 = loop_1.threePointArc((-0.73071, -0.318), (-0.78088, -0.32025))
loop_1 = loop_1.threePointArc((-0.85262, -0.31036), (-0.92467, -0.29323))
loop_1 = loop_1.lineTo(-0.93961, -0.28403)
loop_1 = loop_1.lineTo(-0.95096, -0.26933)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_50_interval_0.stl')