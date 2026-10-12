import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78948, -0.27375)
loop_1 = loop_1.lineTo(-0.80642, -0.28373)
loop_1 = loop_1.lineTo(-0.79056, -0.30059)
loop_1 = loop_1.lineTo(-0.7155, -0.29277)
loop_1 = loop_1.lineTo(-0.70829, -0.28023)
loop_1 = loop_1.threePointArc((-0.71376, -0.27999), (-0.71944, -0.27963))
loop_1 = loop_1.lineTo(-0.78941, -0.27375)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.01)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_018/cadfit/raw/part_018/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_018/cadfit/raw/part_018/sketch_14_interval_0.stl')