import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2498, -0.82083, 0.06378), normal=(0.16648, 0.98604, 0.00175), xDir=(0.98604, -0.16648, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.13075, -0.20759)
loop_1 = loop_1.lineTo(-0.20976, -0.21691)
loop_1 = loop_1.lineTo(-0.16071, -0.23645)
loop_1 = loop_1.lineTo(-0.13074, -0.23229)
loop_1 = loop_1.lineTo(-0.11795, -0.21789)
loop_1 = loop_1.lineTo(-0.12995, -0.20823)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_018/cadfit/raw/part_018/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_018/cadfit/raw/part_018/sketch_11_interval_0.stl')