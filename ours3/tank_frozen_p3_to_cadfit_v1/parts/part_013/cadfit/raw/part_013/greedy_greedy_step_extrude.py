import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33241, -0.52713, 0.0443), normal=(0.59987, 0.80009, 0.00268), xDir=(0.8001, -0.59987, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40695, -0.31441)
loop_1 = loop_1.lineTo(-0.47558, -0.31441)
loop_1 = loop_1.lineTo(-0.47439, -0.32684)
loop_1 = loop_1.lineTo(-0.40443, -0.32676)
loop_1 = loop_1.lineTo(-0.38266, -0.32603)
loop_1 = loop_1.lineTo(-0.40579, -0.31452)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.48)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/greedy_greedy_step_extrude.stl')