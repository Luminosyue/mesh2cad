import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11267, -0.43146, 0.66458), normal=(-0.9393, 0.34311, 0.00069), xDir=(0.34311, 0.9393, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09838, 1.43408)
loop_1 = loop_1.lineTo(0.12442, 1.43532)
loop_1 = loop_1.lineTo(0.15167, 1.44324)
loop_1 = loop_1.lineTo(0.16512, 1.45692)
loop_1 = loop_1.lineTo(0.02647, 1.46485)
loop_1 = loop_1.lineTo(0.09769, 1.43438)
loop_1 = loop_1.threePointArc((0.07878, 1.43363), (0.06278, 1.43275))
loop_1 = loop_1.threePointArc((0.05557, 1.43241), (0.05067, 1.43207))
loop_1 = loop_1.lineTo(0.05067, 1.40941)
loop_1 = loop_1.lineTo(0.05955, 1.42156)
loop_1 = loop_1.lineTo(0.06993, 1.42849)
loop_1 = loop_1.lineTo(0.09718, 1.43403)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_12_interval_0.stl')