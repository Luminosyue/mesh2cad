import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01789, -0.91848, -0.03254), normal=(-0.03729, 0.73508, 0.67696), xDir=(0.99872, 0.05067, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03067, 0.0269)
loop_1 = loop_1.lineTo(-0.03371, -0.06451)
loop_1 = loop_1.lineTo(-0.03395, -0.08422)
loop_1 = loop_1.lineTo(-0.0284, -0.09642)
loop_1 = loop_1.lineTo(-0.01781, -0.10309)
loop_1 = loop_1.lineTo(0.02462, -0.10741)
loop_1 = loop_1.threePointArc((0.03444, -0.10684), (0.04245, -0.10639))
loop_1 = loop_1.lineTo(0.0591, -0.08422)
loop_1 = loop_1.lineTo(0.0606, -0.05823)
loop_1 = loop_1.lineTo(0.06337, 0.02228)
loop_1 = loop_1.lineTo(0.06215, 0.03653)
loop_1 = loop_1.lineTo(0.05529, 0.04917)
loop_1 = loop_1.threePointArc((0.03805, 0.05641), (0.03026, 0.05705))
loop_1 = loop_1.lineTo(-0.0037, 0.05853)
loop_1 = loop_1.lineTo(-0.03067, 0.0269)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/sketch_0_interval_0.stl')