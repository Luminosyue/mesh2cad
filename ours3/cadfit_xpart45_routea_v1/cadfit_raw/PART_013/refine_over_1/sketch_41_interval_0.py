import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5823, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56627, 0.2054)
loop_1 = loop_1.lineTo(0.79941, 0.21644)
loop_1 = loop_1.lineTo(0.47779, 0.2054)
loop_1 = loop_1.lineTo(0.22826, 0.20476)
loop_1 = loop_1.lineTo(0.25627, 0.20212)
loop_1 = loop_1.threePointArc((0.33479, 0.20316), (0.416, 0.20221))
loop_1 = loop_1.lineTo(0.79883, 0.19868)
loop_1 = loop_1.threePointArc((0.78942, 0.20033), (0.78087, 0.2012))
loop_1 = loop_1.threePointArc((0.77221, 0.20249), (0.76443, 0.20315))
loop_1 = loop_1.lineTo(0.80811, 0.20381)
loop_1 = loop_1.lineTo(0.56687, 0.2054)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_41_interval_0.stl')