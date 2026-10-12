import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.70376, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06333, -0.26901)
loop_1 = loop_1.lineTo(0.06193, -0.77)
loop_1 = loop_1.lineTo(0.04478, -0.76965)
loop_1 = loop_1.threePointArc((0.04373, -0.74395), (0.04169, -0.71967))
loop_1 = loop_1.threePointArc((0.03959, -0.69612), (0.03551, -0.67413))
loop_1 = loop_1.threePointArc((0.03135, -0.65715), (0.02918, -0.63944))
loop_1 = loop_1.threePointArc((0.02904, -0.61286), (0.02997, -0.58556))
loop_1 = loop_1.threePointArc((0.03033, -0.55795), (0.03006, -0.53178))
loop_1 = loop_1.threePointArc((0.03038, -0.50113), (0.02982, -0.47204))
loop_1 = loop_1.threePointArc((0.02901, -0.41294), (0.02932, -0.35172))
loop_1 = loop_1.threePointArc((0.0298, -0.3388), (0.03085, -0.32574))
loop_1 = loop_1.threePointArc((0.03141, -0.31839), (0.0332, -0.31129))
loop_1 = loop_1.lineTo(0.03612, -0.29944)
loop_1 = loop_1.lineTo(0.05202, -0.27866)
loop_1 = loop_1.threePointArc((0.05786, -0.27383), (0.06308, -0.26925))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_24_interval_0.stl')