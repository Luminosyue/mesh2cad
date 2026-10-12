import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.97526, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02471, -0.21359)
loop_1 = loop_1.lineTo(-0.0414, -0.23693)
loop_1 = loop_1.threePointArc((-0.04754, -0.24551), (-0.05013, -0.24846))
loop_1 = loop_1.lineTo(-0.07574, -0.27283)
loop_1 = loop_1.threePointArc((-0.08426, -0.27942), (-0.09004, -0.28322))
loop_1 = loop_1.threePointArc((-0.10065, -0.28556), (-0.11161, -0.28783))
loop_1 = loop_1.lineTo(-0.12223, -0.29021)
loop_1 = loop_1.lineTo(-0.02471, -0.28918)
loop_1 = loop_1.lineTo(-0.02471, -0.21369)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_34_interval_0.stl')