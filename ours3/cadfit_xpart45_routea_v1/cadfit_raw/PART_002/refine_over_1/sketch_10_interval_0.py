import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.27026, -0.09295, 0.34528), normal=(-0.14906, -0.98883, 2e-05), xDir=(-0.98883, 0.14906, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05365, -0.58506)
loop_1 = loop_1.lineTo(-0.07338, -0.59845)
loop_1 = loop_1.lineTo(-0.08936, -0.60673)
loop_1 = loop_1.lineTo(-0.11177, -0.61609)
loop_1 = loop_1.lineTo(-0.12399, -0.62028)
loop_1 = loop_1.threePointArc((-0.1469, -0.62683), (-0.16808, -0.63239))
loop_1 = loop_1.lineTo(-0.21764, -0.63894)
loop_1 = loop_1.lineTo(-0.25623, -0.6435)
loop_1 = loop_1.lineTo(-0.28488, -0.6445)
loop_1 = loop_1.threePointArc((-0.29538, -0.6441), (-0.30294, -0.64387))
loop_1 = loop_1.lineTo(-0.27464, -0.64608)
loop_1 = loop_1.lineTo(-0.05365, -0.64991)
loop_1 = loop_1.lineTo(-0.05365, -0.58835)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_10_interval_0.stl')