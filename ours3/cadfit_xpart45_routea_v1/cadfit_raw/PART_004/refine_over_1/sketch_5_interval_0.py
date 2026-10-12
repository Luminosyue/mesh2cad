import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2498, -0.37491, -0.25719), normal=(-0.21544, 0.97652, 0.00087), xDir=(0.97652, 0.21544, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.60074, -0.73149)
loop_1 = loop_1.threePointArc((0.6014, -0.75403), (0.60141, -0.77752))
loop_1 = loop_1.lineTo(0.60215, -1.03856)
loop_1 = loop_1.lineTo(0.60023, -1.07421)
loop_1 = loop_1.lineTo(0.59691, -1.1069)
loop_1 = loop_1.lineTo(0.58946, -1.11753)
loop_1 = loop_1.threePointArc((0.58213, -1.12968), (0.57595, -1.14182))
loop_1 = loop_1.lineTo(0.56629, -1.0901)
loop_1 = loop_1.lineTo(0.56776, -1.07033)
loop_1 = loop_1.threePointArc((0.56727, -1.03483), (0.56713, -1.00051))
loop_1 = loop_1.lineTo(0.56607, -0.97098)
loop_1 = loop_1.lineTo(0.56594, -0.93783)
loop_1 = loop_1.lineTo(0.56648, -0.92033)
loop_1 = loop_1.lineTo(0.56564, -0.82582)
loop_1 = loop_1.lineTo(0.59926, -0.73552)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_interval_0.stl')