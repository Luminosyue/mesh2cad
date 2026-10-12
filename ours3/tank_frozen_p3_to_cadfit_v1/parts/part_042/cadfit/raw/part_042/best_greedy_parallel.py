import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.07, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80494, 0.28646)
loop_1 = loop_1.lineTo(0.78868, 0.28632)
loop_1 = loop_1.threePointArc((0.78953, 0.27502), (0.79322, 0.27368))
loop_1 = loop_1.lineTo(0.82049, 0.26345)
loop_1 = loop_1.lineTo(0.83119, 0.25954)
loop_1 = loop_1.threePointArc((0.83745, 0.25707), (0.8434, 0.25484))
loop_1 = loop_1.lineTo(0.85751, 0.24998)
loop_1 = loop_1.lineTo(0.88419, 0.23731)
loop_1 = loop_1.lineTo(0.90754, 0.2288)
loop_1 = loop_1.lineTo(0.90978, 0.23904)
loop_1 = loop_1.lineTo(0.88908, 0.24817)
loop_1 = loop_1.threePointArc((0.87912, 0.25528), (0.86889, 0.2627))
loop_1 = loop_1.lineTo(0.83616, 0.27504)
loop_1 = loop_1.lineTo(0.82331, 0.28039)
loop_1 = loop_1.lineTo(0.80708, 0.28547)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_042/cadfit/raw/part_042/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_042/cadfit/raw/part_042/sketch_3_interval_0.stl')