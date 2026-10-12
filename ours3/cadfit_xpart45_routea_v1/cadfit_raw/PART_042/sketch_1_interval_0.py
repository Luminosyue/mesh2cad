import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.09103, 0.28416, 0.00229), normal=(0.02355, -0.99972, -0.0022), xDir=(-0.99972, -0.02355, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1684, 0.01907)
loop_1 = loop_1.lineTo(-0.13763, 0.00819)
loop_1 = loop_1.lineTo(-0.13638, -0.02585)
loop_1 = loop_1.lineTo(-0.16745, -0.04159)
loop_1 = loop_1.lineTo(-0.18247, -0.03802)
loop_1 = loop_1.lineTo(-0.19444, 0.00449)
loop_1 = loop_1.lineTo(-0.18526, 0.01635)
loop_1 = loop_1.lineTo(-0.1684, 0.01907)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_1_interval_0.stl')