import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.10787, -0.00334, -0.21379), normal=(0.00044, 0.00044, -1.0), xDir=(0.0, -1.0, -0.00044))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19119, 0.03028)
loop_1 = loop_1.lineTo(0.22359, -0.02317)
loop_1 = loop_1.threePointArc((0.22569, -0.06649), (0.22766, -0.10372))
loop_1 = loop_1.lineTo(0.19487, -0.16873)
loop_1 = loop_1.lineTo(0.17713, -0.18566)
loop_1 = loop_1.lineTo(0.11064, -0.20791)
loop_1 = loop_1.threePointArc((0.06744, -0.20206), (0.03009, -0.19722))
loop_1 = loop_1.lineTo(0.01022, -0.18427)
loop_1 = loop_1.lineTo(-0.05064, -0.10372)
loop_1 = loop_1.lineTo(-0.04559, -0.02317)
loop_1 = loop_1.threePointArc((-0.0096, 0.01806), (0.02477, 0.05737))
loop_1 = loop_1.threePointArc((0.06954, 0.06492), (0.11064, 0.06933))
loop_1 = loop_1.lineTo(0.14949, 0.05738)
loop_1 = loop_1.lineTo(0.18764, 0.03258)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_033/cadfit/raw/part_033/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_033/cadfit/raw/part_033/sketch_0_interval_0.stl')