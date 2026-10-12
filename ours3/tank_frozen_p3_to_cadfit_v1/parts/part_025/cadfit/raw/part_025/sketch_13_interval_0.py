import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33297, -0.27535, 0.4006), normal=(0.06909, 0.16922, -0.98315), xDir=(0.0, -0.98551, -0.16962))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20662, 0.46826)
loop_1 = loop_1.lineTo(-0.21329, 0.45612)
loop_1 = loop_1.lineTo(-0.22233, 0.44032)
loop_1 = loop_1.lineTo(-0.2418, 0.43983)
loop_1 = loop_1.lineTo(-0.25825, 0.46279)
loop_1 = loop_1.lineTo(-0.26064, 0.47348)
loop_1 = loop_1.lineTo(-0.26277, 0.49621)
loop_1 = loop_1.lineTo(-0.25202, 0.50092)
loop_1 = loop_1.lineTo(-0.22947, 0.50373)
loop_1 = loop_1.lineTo(-0.21678, 0.48107)
loop_1 = loop_1.lineTo(-0.20722, 0.46902)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_13_interval_0.stl')