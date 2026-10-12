import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04205, 0.50483)
loop_1 = loop_1.lineTo(0.12735, 0.50372)
loop_1 = loop_1.threePointArc((0.13367, 0.50108), (0.13899, 0.49778))
loop_1 = loop_1.threePointArc((0.142, 0.4886), (0.14524, 0.48071))
loop_1 = loop_1.threePointArc((0.14582, 0.01007), (0.14523, -0.47911))
loop_1 = loop_1.threePointArc((0.14401, -0.48641), (0.14077, -0.49226))
loop_1 = loop_1.threePointArc((0.12215, -0.50414), (0.10838, -0.50433))
loop_1 = loop_1.threePointArc((0.00072, -0.50505), (-0.1105, -0.50443))
loop_1 = loop_1.lineTo(-0.13586, -0.50196)
loop_1 = loop_1.lineTo(-0.14528, -0.47764)
loop_1 = loop_1.lineTo(-0.14441, 0.48993)
loop_1 = loop_1.lineTo(-0.13643, 0.50067)
loop_1 = loop_1.threePointArc((-0.10332, 0.50454), (-0.07775, 0.50408))
loop_1 = loop_1.lineTo(0.04117, 0.50483)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.98)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/dvd_player_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_000/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/dvd_player_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_000/sketch_5_interval_0.stl')