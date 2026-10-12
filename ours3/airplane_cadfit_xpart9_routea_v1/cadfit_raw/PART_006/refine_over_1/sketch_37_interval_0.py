import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.01105, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.90101, 0.2114)
loop_1 = loop_1.lineTo(-0.46963, 0.13871)
loop_1 = loop_1.lineTo(-0.15129, 0.14395)
loop_1 = loop_1.lineTo(-0.01541, 0.14579)
loop_1 = loop_1.lineTo(0.29587, 0.15385)
loop_1 = loop_1.lineTo(0.52789, 0.15785)
loop_1 = loop_1.lineTo(0.72421, 0.1615)
loop_1 = loop_1.lineTo(0.80761, 0.16208)
loop_1 = loop_1.threePointArc((0.83441, 0.15836), (0.86069, 0.15139))
loop_1 = loop_1.threePointArc((0.88104, 0.1464), (0.90095, 0.14035))
loop_1 = loop_1.lineTo(0.90106, 0.21042)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_37_interval_0.stl')