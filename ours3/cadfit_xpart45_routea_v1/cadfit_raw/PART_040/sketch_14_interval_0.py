import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34274, 0.18883)
loop_1 = loop_1.lineTo(0.3572, 0.18656)
loop_1 = loop_1.lineTo(0.37522, 0.17675)
loop_1 = loop_1.threePointArc((0.38722, 0.15873), (0.38966, 0.15065))
loop_1 = loop_1.lineTo(0.38341, 0.13665)
loop_1 = loop_1.lineTo(0.3756, 0.1247)
loop_1 = loop_1.lineTo(0.35912, 0.10883)
loop_1 = loop_1.lineTo(0.34766, 0.10455)
loop_1 = loop_1.threePointArc((0.33678, 0.10432), (0.33116, 0.10585))
loop_1 = loop_1.lineTo(0.31648, 0.11424)
loop_1 = loop_1.threePointArc((0.30665, 0.12583), (0.30386, 0.12933))
loop_1 = loop_1.lineTo(0.29517, 0.15099)
loop_1 = loop_1.threePointArc((0.29626, 0.15622), (0.2971, 0.16118))
loop_1 = loop_1.threePointArc((0.30213, 0.17109), (0.30561, 0.17468))
loop_1 = loop_1.lineTo(0.32143, 0.18326)
loop_1 = loop_1.lineTo(0.33962, 0.18725)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/sketch_14_interval_0.stl')