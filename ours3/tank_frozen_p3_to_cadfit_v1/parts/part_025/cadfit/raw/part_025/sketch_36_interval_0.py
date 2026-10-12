import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.30437, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.09627, 0.0388)
loop_1 = loop_1.lineTo(-0.0375, 0.03857)
loop_1 = loop_1.lineTo(-0.03774, -0.07272)
loop_1 = loop_1.lineTo(-0.09948, -0.07249)
loop_1 = loop_1.lineTo(-0.09808, -0.04404)
loop_1 = loop_1.lineTo(-0.09749, -0.01639)
loop_1 = loop_1.lineTo(-0.09679, 0.01148)
loop_1 = loop_1.lineTo(-0.09627, 0.03869)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_36_interval_0.stl')