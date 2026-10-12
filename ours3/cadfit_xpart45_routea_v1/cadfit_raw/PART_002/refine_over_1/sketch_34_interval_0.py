import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.48355, -0.40892, 0.30864), normal=(0.922, 0.3872, -0.00028), xDir=(0.3872, -0.922, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16447, 1.07833)
loop_1 = loop_1.lineTo(-0.20496, 1.07833)
loop_1 = loop_1.lineTo(-0.20493, 1.02413)
loop_1 = loop_1.threePointArc((-0.19142, 1.04344), (-0.1797, 1.06023))
loop_1 = loop_1.threePointArc((-0.17194, 1.06943), (-0.16501, 1.07768))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_34_interval_0.stl')