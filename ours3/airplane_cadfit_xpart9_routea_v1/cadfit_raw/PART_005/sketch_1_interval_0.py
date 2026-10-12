import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0049, 0.26474, -0.07581), normal=(0.86818, -0.10858, -0.48423), xDir=(-0.1241, -0.99227, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.19495, -0.10904)
loop_1 = loop_1.threePointArc((1.21014, -0.11122), (1.21532, -0.1125))
loop_1 = loop_1.lineTo(1.21373, -0.17751)
loop_1 = loop_1.lineTo(1.20251, -0.1809)
loop_1 = loop_1.lineTo(1.15461, -0.14499)
loop_1 = loop_1.lineTo(1.15442, -0.13445)
loop_1 = loop_1.lineTo(1.17347, -0.11258)
loop_1 = loop_1.lineTo(1.19495, -0.10904)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/sketch_1_interval_0.stl')