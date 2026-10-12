import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04201, 0.44959, 0.40501), normal=(-3e-05, -0.69093, 0.72292), xDir=(-1.0, 5e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.88482, 0.7111)
loop_1 = loop_1.lineTo(0.87045, 0.6836)
loop_1 = loop_1.lineTo(0.85756, 0.66199)
loop_1 = loop_1.lineTo(0.83452, 0.6372)
loop_1 = loop_1.lineTo(0.81831, 0.61364)
loop_1 = loop_1.lineTo(0.82155, 0.58315)
loop_1 = loop_1.threePointArc((0.82712, 0.56924), (0.8318, 0.55785))
loop_1 = loop_1.lineTo(0.8529, 0.53477)
loop_1 = loop_1.lineTo(0.86898, 0.5172)
loop_1 = loop_1.lineTo(0.851, 0.55241)
loop_1 = loop_1.lineTo(0.85299, 0.60502)
loop_1 = loop_1.lineTo(0.88475, 0.71087)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_20_interval_0.stl')