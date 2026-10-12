import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64526, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10622, -0.00032)
loop_1 = loop_1.lineTo(0.10575, -0.17)
loop_1 = loop_1.lineTo(0.00551, -0.1696)
loop_1 = loop_1.threePointArc((0.01612, -0.15291), (0.02594, -0.13683))
loop_1 = loop_1.threePointArc((0.04387, -0.10679), (0.06259, -0.0757))
loop_1 = loop_1.threePointArc((0.06839, -0.06537), (0.07471, -0.05495))
loop_1 = loop_1.lineTo(0.10404, -0.00434)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_31_interval_0.stl')