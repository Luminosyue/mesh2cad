import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2915, -0.13777, 0.33514), normal=(0.06908, 0.16949, 0.98311), xDir=(0.0, 0.98546, -0.1699))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25059, 0.46592)
loop_1 = loop_1.lineTo(0.2535, 0.48584)
loop_1 = loop_1.lineTo(0.23556, 0.49358)
loop_1 = loop_1.lineTo(0.21869, 0.49517)
loop_1 = loop_1.lineTo(0.20856, 0.48584)
loop_1 = loop_1.lineTo(0.20451, 0.47217)
loop_1 = loop_1.lineTo(0.19355, 0.45789)
loop_1 = loop_1.threePointArc((0.20163, 0.44378), (0.20944, 0.42994))
loop_1 = loop_1.lineTo(0.21955, 0.42367)
loop_1 = loop_1.lineTo(0.23488, 0.42995)
loop_1 = loop_1.lineTo(0.24305, 0.44238)
loop_1 = loop_1.lineTo(0.25059, 0.46592)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_2_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_2_interval_1.stl')