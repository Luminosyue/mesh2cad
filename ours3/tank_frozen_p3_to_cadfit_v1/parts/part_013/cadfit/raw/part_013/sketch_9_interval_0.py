import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.43279, 1.05737, -0.19768), normal=(0.18551, -0.98264, -9e-05), xDir=(-0.98264, -0.18551, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82436, -0.52969)
loop_1 = loop_1.lineTo(0.84526, -0.53611)
loop_1 = loop_1.lineTo(0.86451, -0.56933)
loop_1 = loop_1.lineTo(0.84526, -0.57136)
loop_1 = loop_1.lineTo(0.82436, -0.57246)
loop_1 = loop_1.lineTo(0.66864, -0.57246)
loop_1 = loop_1.lineTo(0.67095, -0.55368)
loop_1 = loop_1.threePointArc((0.71927, -0.55162), (0.76962, -0.54979))
loop_1 = loop_1.lineTo(0.82225, -0.53047)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_9_interval_0.stl')