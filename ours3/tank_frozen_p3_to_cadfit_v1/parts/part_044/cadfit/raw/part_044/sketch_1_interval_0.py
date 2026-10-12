import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.67374, -0.03869, 0.32227), normal=(-0.00296, 0.96634, -0.25726), xDir=(1.0, 0.00306, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04057, 0.11383)
loop_1 = loop_1.lineTo(0.06032, 0.11038)
loop_1 = loop_1.lineTo(0.07288, 0.10513)
loop_1 = loop_1.lineTo(0.06891, 0.07912)
loop_1 = loop_1.lineTo(0.0406, 0.07431)
loop_1 = loop_1.lineTo(0.00829, 0.08294)
loop_1 = loop_1.lineTo(0.01124, 0.09782)
loop_1 = loop_1.threePointArc((0.02521, 0.10545), (0.03977, 0.11339))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_1_interval_0.stl')