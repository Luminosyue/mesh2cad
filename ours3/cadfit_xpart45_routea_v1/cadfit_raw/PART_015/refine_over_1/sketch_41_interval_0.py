import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.2164), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77674, -0.54208)
loop_1 = loop_1.lineTo(0.82569, -0.54193)
loop_1 = loop_1.lineTo(0.82551, -0.46206)
loop_1 = loop_1.threePointArc((0.81834, -0.47444), (0.81072, -0.48717))
loop_1 = loop_1.threePointArc((0.80035, -0.50473), (0.7905, -0.52158))
loop_1 = loop_1.lineTo(0.78109, -0.53588)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_41_interval_0.stl')