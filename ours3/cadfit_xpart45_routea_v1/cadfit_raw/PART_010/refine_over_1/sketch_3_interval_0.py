import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.63254, -0.22459, -0.05956), normal=(-0.91693, -0.00087, 0.39905), xDir=(-0.00095, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35129, -0.70541)
loop_1 = loop_1.lineTo(0.35128, -0.73565)
loop_1 = loop_1.lineTo(0.46048, -0.73564)
loop_1 = loop_1.lineTo(0.43937, -0.7324)
loop_1 = loop_1.lineTo(0.42845, -0.72581)
loop_1 = loop_1.lineTo(0.40174, -0.71705)
loop_1 = loop_1.lineTo(0.37044, -0.70817)
loop_1 = loop_1.lineTo(0.35266, -0.70549)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_3_interval_0.stl')