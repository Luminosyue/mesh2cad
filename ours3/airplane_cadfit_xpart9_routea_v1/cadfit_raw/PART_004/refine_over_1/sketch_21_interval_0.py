import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.13715, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00295, 0.04051)
loop_1 = loop_1.lineTo(0.94, 0.03805)
loop_1 = loop_1.lineTo(0.93963, 0.0236)
loop_1 = loop_1.lineTo(0.92532, 0.03457)
loop_1 = loop_1.threePointArc((0.91937, 0.03612), (0.91347, 0.03636))
loop_1 = loop_1.lineTo(0.89825, 0.0382)
loop_1 = loop_1.threePointArc((0.86685, 0.03838), (0.8373, 0.03766))
loop_1 = loop_1.threePointArc((0.79557, 0.03696), (0.75274, 0.03675))
loop_1 = loop_1.threePointArc((0.67662, 0.03505), (0.60419, 0.03229))
loop_1 = loop_1.lineTo(0.50707, 0.02957)
loop_1 = loop_1.threePointArc((0.44117, 0.03057), (0.3785, 0.03089))
loop_1 = loop_1.threePointArc((0.3076, 0.03315), (0.23446, 0.03616))
loop_1 = loop_1.threePointArc((0.2132, 0.03666), (0.19338, 0.03658))
loop_1 = loop_1.threePointArc((0.09621, 0.03915), (0.00355, 0.04032))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_21_interval_0.stl')