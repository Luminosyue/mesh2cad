import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69634, 0.42672, 0.49536), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.25201, -0.09601)
loop_1 = loop_1.lineTo(-0.22359, -0.10211)
loop_1 = loop_1.lineTo(-0.19628, -0.11959)
loop_1 = loop_1.lineTo(-0.34384, -0.11959)
loop_1 = loop_1.lineTo(-0.33072, -0.11375)
loop_1 = loop_1.lineTo(-0.29481, -0.098)
loop_1 = loop_1.threePointArc((-0.27687, -0.09607), (-0.2599, -0.09481))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_5_interval_0.stl')