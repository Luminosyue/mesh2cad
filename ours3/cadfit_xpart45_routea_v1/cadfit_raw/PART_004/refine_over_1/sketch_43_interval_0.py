import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.80257), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17071, 0.40226)
loop_1 = loop_1.lineTo(0.13028, 0.40157)
loop_1 = loop_1.lineTo(0.13007, 0.36579)
loop_1 = loop_1.lineTo(0.10558, 0.37524)
loop_1 = loop_1.lineTo(0.07081, 0.38599)
loop_1 = loop_1.lineTo(0.03553, 0.3938)
loop_1 = loop_1.lineTo(0.00093, 0.39879)
loop_1 = loop_1.threePointArc((-0.04177, 0.40062), (-0.08257, 0.40139))
loop_1 = loop_1.lineTo(-0.09489, 0.4015)
loop_1 = loop_1.threePointArc((-0.12605, 0.40167), (-0.15827, 0.40217))
loop_1 = loop_1.lineTo(-0.17048, 0.40225)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_43_interval_0.stl')