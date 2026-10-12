import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57883, 0.14879, 0.22932), normal=(0.41386, 0.91034, 3e-05), xDir=(0.91034, -0.41386, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11493, 0.45648)
loop_1 = loop_1.lineTo(0.11474, -0.3523)
loop_1 = loop_1.lineTo(0.11182, -0.36623)
loop_1 = loop_1.lineTo(0.09476, -0.35161)
loop_1 = loop_1.lineTo(0.09467, 0.43132)
loop_1 = loop_1.lineTo(0.10306, 0.4448)
loop_1 = loop_1.lineTo(0.11384, 0.42573)
loop_1 = loop_1.lineTo(0.11383, 0.45599)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_0_interval_0.stl')