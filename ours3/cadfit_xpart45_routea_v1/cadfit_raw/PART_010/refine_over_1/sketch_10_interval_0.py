import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.75451, -0.32051, 0.38128), normal=(0.14782, 0.00235, 0.98901), xDir=(0.0, 1.0, -0.00238))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.73653, -0.20458)
loop_1 = loop_1.lineTo(0.73646, -0.02413)
loop_1 = loop_1.lineTo(0.61799, -0.02454)
loop_1 = loop_1.lineTo(0.64385, -0.0375)
loop_1 = loop_1.lineTo(0.65519, -0.04971)
loop_1 = loop_1.threePointArc((0.66728, -0.0692), (0.67802, -0.08655))
loop_1 = loop_1.lineTo(0.68091, -0.09867)
loop_1 = loop_1.lineTo(0.68395, -0.11585)
loop_1 = loop_1.lineTo(0.68427, -0.12682)
loop_1 = loop_1.lineTo(0.68032, -0.14398)
loop_1 = loop_1.lineTo(0.67546, -0.16022)
loop_1 = loop_1.lineTo(0.66372, -0.17373)
loop_1 = loop_1.lineTo(0.64391, -0.19386)
loop_1 = loop_1.lineTo(0.62778, -0.20064)
loop_1 = loop_1.lineTo(0.61587, -0.20444)
loop_1 = loop_1.lineTo(0.73324, -0.20457)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_10_interval_0.stl')