import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.09632, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12961, 0.44391)
loop_1 = loop_1.lineTo(-0.15806, 0.4372)
loop_1 = loop_1.lineTo(-0.1696, 0.42939)
loop_1 = loop_1.lineTo(-0.18045, 0.42039)
loop_1 = loop_1.lineTo(-0.16461, 0.3879)
loop_1 = loop_1.lineTo(-0.12917, 0.37657)
loop_1 = loop_1.threePointArc((-0.10504, 0.37933), (-0.08981, 0.38095))
loop_1 = loop_1.lineTo(-0.06228, 0.3842)
loop_1 = loop_1.lineTo(-0.02484, 0.3881)
loop_1 = loop_1.lineTo(0.00594, 0.40992)
loop_1 = loop_1.lineTo(0.01934, 0.42051)
loop_1 = loop_1.lineTo(0.00485, 0.42258)
loop_1 = loop_1.threePointArc((-0.00109, 0.42331), (-0.00709, 0.42428))
loop_1 = loop_1.lineTo(-0.0253, 0.42847)
loop_1 = loop_1.lineTo(-0.06183, 0.43462)
loop_1 = loop_1.lineTo(-0.09413, 0.43971)
loop_1 = loop_1.lineTo(-0.12674, 0.44388)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_2_interval_0.stl')