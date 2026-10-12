import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2935, 0.63147, 0.00137), normal=(-0.364, 0.9314, -0.00081), xDir=(0.9314, 0.364, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19514, -0.25033)
loop_1 = loop_1.lineTo(0.15694, -0.28346)
loop_1 = loop_1.lineTo(0.19629, -0.32921)
loop_1 = loop_1.lineTo(0.20683, -0.33129)
loop_1 = loop_1.lineTo(0.28809, -0.29897)
loop_1 = loop_1.lineTo(0.29976, -0.28346)
loop_1 = loop_1.lineTo(0.28808, -0.27234)
loop_1 = loop_1.lineTo(0.25284, -0.26952)
loop_1 = loop_1.lineTo(0.20232, -0.24724)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_018/cadfit/raw/part_018/sketch_12_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_018/cadfit/raw/part_018/sketch_12_interval_1.stl')