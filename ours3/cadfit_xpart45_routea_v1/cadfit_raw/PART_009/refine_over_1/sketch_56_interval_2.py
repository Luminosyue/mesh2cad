import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.93604, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.45989, -0.52818)
loop_1 = loop_1.lineTo(0.41337, -0.46773)
loop_1 = loop_1.threePointArc((0.41036, -0.46205), (0.40692, -0.45757))
loop_1 = loop_1.threePointArc((0.39418, -0.43983), (0.38122, -0.42403))
loop_1 = loop_1.lineTo(0.35529, -0.40882)
loop_1 = loop_1.lineTo(0.30549, -0.41336)
loop_1 = loop_1.lineTo(0.24922, -0.42051)
loop_1 = loop_1.lineTo(0.19829, -0.42401)
loop_1 = loop_1.lineTo(0.13713, -0.42307)
loop_1 = loop_1.lineTo(0.09705, -0.42186)
loop_1 = loop_1.lineTo(0.04224, -0.42011)
loop_1 = loop_1.threePointArc((-0.06212, -0.41849), (-0.16177, -0.42091))
loop_1 = loop_1.lineTo(-0.21117, -0.41796)
loop_1 = loop_1.lineTo(-0.2636, -0.41195)
loop_1 = loop_1.lineTo(-0.31431, -0.40479)
loop_1 = loop_1.lineTo(0.45988, -0.52818)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_56_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_56_interval_2.stl')