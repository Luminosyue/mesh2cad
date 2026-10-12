import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.83929), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05475, 0.42496)
loop_1 = loop_1.lineTo(0.14082, 0.55479)
loop_1 = loop_1.lineTo(0.12931, 0.54426)
loop_1 = loop_1.lineTo(0.10652, 0.53442)
loop_1 = loop_1.lineTo(0.08872, 0.52831)
loop_1 = loop_1.lineTo(0.06781, 0.50838)
loop_1 = loop_1.threePointArc((0.06401, 0.49804), (0.06073, 0.48811))
loop_1 = loop_1.lineTo(0.05603, 0.47355)
loop_1 = loop_1.lineTo(0.0535, 0.45911)
loop_1 = loop_1.threePointArc((0.05192, 0.44376), (0.05023, 0.42789))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_48_interval_0.stl')