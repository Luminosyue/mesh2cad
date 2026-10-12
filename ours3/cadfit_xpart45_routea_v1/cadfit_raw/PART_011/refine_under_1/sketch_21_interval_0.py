import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.79176, -0.44409, -0.01475), normal=(-0.89584, 0.44438, 0.00038), xDir=(0.44438, 0.89584, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15811, 0.22109)
loop_1 = loop_1.threePointArc((0.15918, 0.08404), (0.16075, -0.04752))
loop_1 = loop_1.lineTo(0.16308, -0.18891)
loop_1 = loop_1.lineTo(-0.23706, -0.18891)
loop_1 = loop_1.lineTo(-0.23101, -0.12091)
loop_1 = loop_1.lineTo(-0.1859, 0.22109)
loop_1 = loop_1.lineTo(0.14997, 0.22109)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_21_interval_0.stl')