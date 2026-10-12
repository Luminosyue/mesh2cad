import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.77628, 0.28401, 0.05724), normal=(0.91025, -0.41398, -0.00793), xDir=(-0.41399, -0.91028, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30586, -0.20284)
loop_1 = loop_1.lineTo(-0.31809, 0.20717)
loop_1 = loop_1.lineTo(-0.23771, 0.20717)
loop_1 = loop_1.lineTo(-0.23079, 0.24883)
loop_1 = loop_1.lineTo(-0.03406, 0.25522)
loop_1 = loop_1.lineTo(-0.01379, 0.23586)
loop_1 = loop_1.lineTo(-0.01163, 0.20717)
loop_1 = loop_1.lineTo(0.35526, 0.20717)
loop_1 = loop_1.lineTo(0.36956, -0.20284)
loop_1 = loop_1.lineTo(-0.30437, -0.20284)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_41_interval_0.stl')