import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.10742), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08333, 0.65449)
loop_1 = loop_1.lineTo(0.10966, 0.69397)
loop_1 = loop_1.lineTo(0.15957, 0.76714)
loop_1 = loop_1.threePointArc((0.16318, 0.78414), (0.16496, 0.79239))
loop_1 = loop_1.threePointArc((0.17082, 0.81262), (0.17368, 0.82282))
loop_1 = loop_1.lineTo(0.17711, 0.83848)
loop_1 = loop_1.lineTo(0.0834, 0.65461)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_33_interval_0.stl')