import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.68208, -0.20659, 0.02629), normal=(-1.0, -0.0, 0.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.44207, -0.22601)
loop_1 = loop_1.lineTo(-0.41726, -0.23246)
loop_1 = loop_1.lineTo(-0.40425, -0.23393)
loop_1 = loop_1.threePointArc((-0.38225, -0.23417), (-0.36113, -0.23399))
loop_1 = loop_1.threePointArc((-0.27907, -0.2315), (-0.19878, -0.23154))
loop_1 = loop_1.lineTo(-0.03848, -0.23211)
loop_1 = loop_1.threePointArc((0.01652, -0.23306), (0.06419, -0.23257))
loop_1 = loop_1.lineTo(0.08109, -0.23584)
loop_1 = loop_1.lineTo(-0.44207, -0.23586)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_14_interval_0.stl')