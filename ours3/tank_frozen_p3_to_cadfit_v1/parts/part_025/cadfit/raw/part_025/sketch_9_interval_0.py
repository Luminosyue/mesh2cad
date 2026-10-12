import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.1178, -0.12201, 0.32798), normal=(0.54, 0.36703, 0.75743), xDir=(0.56213, -0.82705, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.27912, 0.51696)
loop_1 = loop_1.lineTo(0.23443, 0.49562)
loop_1 = loop_1.lineTo(0.21517, 0.47956)
loop_1 = loop_1.lineTo(0.18421, 0.43672)
loop_1 = loop_1.lineTo(0.17522, 0.39416)
loop_1 = loop_1.lineTo(0.17913, 0.38344)
loop_1 = loop_1.lineTo(0.20082, 0.36486)
loop_1 = loop_1.lineTo(0.23868, 0.37292)
loop_1 = loop_1.lineTo(0.26918, 0.39416)
loop_1 = loop_1.lineTo(0.30541, 0.43686)
loop_1 = loop_1.lineTo(0.31837, 0.47956)
loop_1 = loop_1.lineTo(0.30879, 0.50911)
loop_1 = loop_1.lineTo(0.28107, 0.51644)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_9_interval_0.stl')