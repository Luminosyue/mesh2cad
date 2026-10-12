import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.14218, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08583, 0.47167)
loop_1 = loop_1.lineTo(-0.07379, 0.46566)
loop_1 = loop_1.lineTo(-0.06163, 0.45223)
loop_1 = loop_1.lineTo(-0.05832, 0.42902)
loop_1 = loop_1.lineTo(-0.08525, 0.41465)
loop_1 = loop_1.lineTo(-0.1002, 0.41308)
loop_1 = loop_1.lineTo(-0.11075, 0.41843)
loop_1 = loop_1.lineTo(-0.12121, 0.42192)
loop_1 = loop_1.lineTo(-0.12842, 0.44858)
loop_1 = loop_1.lineTo(-0.12087, 0.46311)
loop_1 = loop_1.lineTo(-0.10147, 0.47089)
loop_1 = loop_1.lineTo(-0.08583, 0.47167)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_35_interval_0.stl')