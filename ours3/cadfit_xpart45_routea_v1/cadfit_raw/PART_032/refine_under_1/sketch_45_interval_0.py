import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25794, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98917, 0.23081)
loop_1 = loop_1.threePointArc((-0.99214, 0.22112), (-0.99442, 0.21166))
loop_1 = loop_1.lineTo(-0.99825, 0.19606)
loop_1 = loop_1.threePointArc((-0.99563, 0.14884), (-0.99233, 0.10377))
loop_1 = loop_1.threePointArc((-0.99154, 0.07759), (-0.99039, 0.05268))
loop_1 = loop_1.lineTo(-0.99012, 0.00475)
loop_1 = loop_1.threePointArc((-0.9905, -0.01896), (-0.99053, -0.04152))
loop_1 = loop_1.lineTo(-0.98943, -0.07507)
loop_1 = loop_1.lineTo(-0.98923, -0.08515)
loop_1 = loop_1.lineTo(-0.98917, 0.2306)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_45_interval_0.stl')