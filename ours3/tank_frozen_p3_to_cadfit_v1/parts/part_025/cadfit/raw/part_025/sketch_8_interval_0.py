import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.1279, -0.12795, -0.31484), normal=(0.54008, 0.36565, -0.75803), xDir=(0.56063, -0.82807, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18541, -0.34185)
loop_1 = loop_1.lineTo(0.22169, -0.34695)
loop_1 = loop_1.lineTo(0.23186, -0.35272)
loop_1 = loop_1.lineTo(0.27567, -0.38653)
loop_1 = loop_1.lineTo(0.29057, -0.40525)
loop_1 = loop_1.threePointArc((0.30097, -0.42037), (0.30955, -0.43271))
loop_1 = loop_1.lineTo(0.32438, -0.46388)
loop_1 = loop_1.lineTo(0.32722, -0.48096)
loop_1 = loop_1.lineTo(0.30965, -0.51833)
loop_1 = loop_1.threePointArc((0.29593, -0.52136), (0.28447, -0.52371))
loop_1 = loop_1.lineTo(0.24908, -0.51344)
loop_1 = loop_1.lineTo(0.23548, -0.50502)
loop_1 = loop_1.threePointArc((0.21885, -0.49026), (0.20812, -0.48096))
loop_1 = loop_1.lineTo(0.17308, -0.43821)
loop_1 = loop_1.lineTo(0.15557, -0.39547)
loop_1 = loop_1.lineTo(0.16045, -0.35881)
loop_1 = loop_1.lineTo(0.18313, -0.3432)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_8_interval_0.stl')