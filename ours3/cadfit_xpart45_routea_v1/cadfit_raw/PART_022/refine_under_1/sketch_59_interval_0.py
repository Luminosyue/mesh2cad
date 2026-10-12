import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.17183), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.8262, 0.54374)
loop_1 = loop_1.lineTo(-0.77629, 0.59596)
loop_1 = loop_1.threePointArc((-0.72185, 0.66128), (-0.66249, 0.72624))
loop_1 = loop_1.threePointArc((-0.57774, 0.79152), (-0.48017, 0.84403))
loop_1 = loop_1.threePointArc((-0.41977, 0.87505), (-0.35446, 0.90061))
loop_1 = loop_1.threePointArc((-0.24639, 0.92274), (-0.13277, 0.93506))
loop_1 = loop_1.threePointArc((-0.21141, 0.92883), (-0.28596, 0.91887))
loop_1 = loop_1.lineTo(-0.33564, 0.9075)
loop_1 = loop_1.lineTo(-0.38288, 0.89335)
loop_1 = loop_1.lineTo(-0.47615, 0.85079)
loop_1 = loop_1.threePointArc((-0.52487, 0.82575), (-0.57033, 0.80038))
loop_1 = loop_1.threePointArc((-0.58418, 0.79224), (-0.596, 0.78318))
loop_1 = loop_1.lineTo(-0.6292, 0.75875)
loop_1 = loop_1.threePointArc((-0.68157, 0.7109), (-0.72905, 0.66281))
loop_1 = loop_1.threePointArc((-0.7515, 0.63632), (-0.77183, 0.6106))
loop_1 = loop_1.lineTo(-0.81217, 0.56212)
loop_1 = loop_1.threePointArc((-0.81955, 0.55288), (-0.82598, 0.54417))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_59_interval_0.stl')