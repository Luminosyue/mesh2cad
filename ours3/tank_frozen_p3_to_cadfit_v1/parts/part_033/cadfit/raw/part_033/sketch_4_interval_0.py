import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11565, -0.09144, -0.22496), normal=(0.00012, 6e-05, 1.0), xDir=(0.0, 1.0, -6e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.68984, 0.76423)
loop_1 = loop_1.lineTo(0.70237, 0.74801)
loop_1 = loop_1.lineTo(0.73804, 0.76423)
loop_1 = loop_1.lineTo(0.70237, 0.83131)
loop_1 = loop_1.lineTo(0.64738, 0.80873)
loop_1 = loop_1.lineTo(0.68896, 0.76516)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_033/cadfit/raw/part_033/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_033/cadfit/raw/part_033/sketch_4_interval_0.stl')