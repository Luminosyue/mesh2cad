import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02437, -0.03524, -0.14844), normal=(-0.00516, 0.87868, 0.47738), xDir=(0.99998, 0.00587, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25117, 0.04291)
loop_1 = loop_1.lineTo(0.2386, 0.03523)
loop_1 = loop_1.lineTo(0.22473, 0.02468)
loop_1 = loop_1.lineTo(0.20204, 0.00987)
loop_1 = loop_1.lineTo(0.18048, -0.00349)
loop_1 = loop_1.lineTo(0.15916, -0.01892)
loop_1 = loop_1.threePointArc((0.15119, -0.02514), (0.14273, -0.03141))
loop_1 = loop_1.lineTo(0.12593, -0.04328)
loop_1 = loop_1.lineTo(0.1023, -0.0592)
loop_1 = loop_1.lineTo(0.10279, -0.08223)
loop_1 = loop_1.lineTo(0.29682, -0.08223)
loop_1 = loop_1.threePointArc((0.29259, -0.06536), (0.28877, -0.05155))
loop_1 = loop_1.lineTo(0.28082, -0.02511)
loop_1 = loop_1.threePointArc((0.27759, -0.01541), (0.27523, -0.00834))
loop_1 = loop_1.threePointArc((0.26368, 0.01824), (0.25245, 0.04062))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_27_interval_0.stl')