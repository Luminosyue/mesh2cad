import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31726, -0.44336)
loop_1 = loop_1.threePointArc((0.31684, -0.45163), (0.31613, -0.46023))
loop_1 = loop_1.threePointArc((0.31182, -0.46933), (0.30787, -0.47731))
loop_1 = loop_1.threePointArc((0.29435, -0.48742), (0.28641, -0.49179))
loop_1 = loop_1.lineTo(0.25013, -0.49203)
loop_1 = loop_1.threePointArc((0.24298, -0.48851), (0.23608, -0.4852))
loop_1 = loop_1.threePointArc((0.22272, -0.46786), (0.21886, -0.46049))
loop_1 = loop_1.threePointArc((0.21804, -0.45113), (0.21725, -0.44357))
loop_1 = loop_1.lineTo(0.22192, -0.4259)
loop_1 = loop_1.threePointArc((0.22862, -0.41915), (0.23569, -0.41222))
loop_1 = loop_1.lineTo(0.25392, -0.40589)
loop_1 = loop_1.threePointArc((0.26149, -0.40522), (0.26938, -0.40466))
loop_1 = loop_1.threePointArc((0.27863, -0.40578), (0.28602, -0.40664))
loop_1 = loop_1.lineTo(0.31311, -0.42833)
loop_1 = loop_1.threePointArc((0.31503, -0.43502), (0.3169, -0.44201))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_30_interval_0.stl')