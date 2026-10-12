import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.74421, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.76712, 0.0545)
loop_1 = loop_1.lineTo(-0.79572, 0.10677)
loop_1 = loop_1.lineTo(-0.79533, 0.00434)
loop_1 = loop_1.lineTo(-0.62842, 0.00468)
loop_1 = loop_1.threePointArc((-0.64783, 0.00958), (-0.6678, 0.01486))
loop_1 = loop_1.lineTo(-0.68071, 0.01831)
loop_1 = loop_1.lineTo(-0.79135, 0.03259)
loop_1 = loop_1.lineTo(-0.78579, 0.07776)
loop_1 = loop_1.lineTo(-0.76725, 0.05464)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_23_interval_0.stl')