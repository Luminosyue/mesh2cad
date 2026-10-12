import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.22609, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.43662, 0.21301)
loop_1 = loop_1.threePointArc((0.44222, 0.21594), (0.44827, 0.21853))
loop_1 = loop_1.threePointArc((0.4558, 0.22226), (0.46241, 0.22637))
loop_1 = loop_1.threePointArc((0.47853, 0.23554), (0.49345, 0.24472))
loop_1 = loop_1.threePointArc((0.50909, 0.25374), (0.52327, 0.26322))
loop_1 = loop_1.lineTo(0.54146, 0.2777)
loop_1 = loop_1.lineTo(0.55914, 0.29027)
loop_1 = loop_1.lineTo(0.58759, 0.31655)
loop_1 = loop_1.lineTo(0.6074, 0.34107)
loop_1 = loop_1.threePointArc((0.61274, 0.35804), (0.61875, 0.37527))
loop_1 = loop_1.lineTo(0.27701, 0.13488)
loop_1 = loop_1.lineTo(0.30538, 0.14662)
loop_1 = loop_1.lineTo(0.33011, 0.15773)
loop_1 = loop_1.lineTo(0.35497, 0.16986)
loop_1 = loop_1.threePointArc((0.3741, 0.18022), (0.39396, 0.19048))
loop_1 = loop_1.threePointArc((0.40495, 0.19578), (0.41492, 0.2014))
loop_1 = loop_1.lineTo(0.43564, 0.21242)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_50_interval_0.stl')