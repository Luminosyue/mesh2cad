import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.11195, -0.04802, -0.52657), normal=(0.00777, 0.03909, 0.99921), xDir=(0.0, 0.99924, -0.03909))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17018, 0.65852)
loop_1 = loop_1.lineTo(0.15813, 0.67083)
loop_1 = loop_1.lineTo(0.13914, 0.67869)
loop_1 = loop_1.lineTo(0.12471, 0.68342)
loop_1 = loop_1.lineTo(0.09681, 0.66201)
loop_1 = loop_1.lineTo(0.08761, 0.63531)
loop_1 = loop_1.lineTo(0.09356, 0.60658)
loop_1 = loop_1.lineTo(0.11851, 0.59141)
loop_1 = loop_1.lineTo(0.14998, 0.60011)
loop_1 = loop_1.threePointArc((0.16023, 0.61921), (0.16399, 0.63064))
loop_1 = loop_1.lineTo(0.16712, 0.64384)
loop_1 = loop_1.lineTo(0.1699, 0.65718)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_20_interval_0.stl')