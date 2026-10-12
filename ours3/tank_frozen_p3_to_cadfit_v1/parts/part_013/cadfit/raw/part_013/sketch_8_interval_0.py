import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.44207, 1.00824, -0.19769), normal=(0.18551, -0.98264, -9e-05), xDir=(-0.98264, -0.18551, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33497, -0.52737)
loop_1 = loop_1.lineTo(0.35815, -0.53823)
loop_1 = loop_1.lineTo(0.39143, -0.535)
loop_1 = loop_1.lineTo(0.45139, -0.54706)
loop_1 = loop_1.lineTo(0.463, -0.56883)
loop_1 = loop_1.threePointArc((0.45765, -0.57086), (0.4514, -0.57246))
loop_1 = loop_1.lineTo(0.28688, -0.57246)
loop_1 = loop_1.lineTo(0.31206, -0.53364)
loop_1 = loop_1.lineTo(0.33305, -0.52745)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_8_interval_0.stl')