import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2382, 0.11496, 0.38421), normal=(5e-05, 6e-05, -1.0), xDir=(0.0, -1.0, -6e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.53855, -0.15548)
loop_1 = loop_1.lineTo(-0.57431, -0.18415)
loop_1 = loop_1.lineTo(-0.5887, -0.18925)
loop_1 = loop_1.lineTo(-0.61928, -0.15548)
loop_1 = loop_1.lineTo(-0.60336, -0.08115)
loop_1 = loop_1.lineTo(-0.5877, -0.05786)
loop_1 = loop_1.lineTo(-0.57724, -0.06256)
loop_1 = loop_1.lineTo(-0.56154, -0.08115)
loop_1 = loop_1.lineTo(-0.55858, -0.09456)
loop_1 = loop_1.lineTo(-0.53906, -0.15392)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_0_interval_0.stl')