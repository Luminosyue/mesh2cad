import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.90763), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13753, 0.54811)
loop_1 = loop_1.lineTo(0.05981, 0.43186)
loop_1 = loop_1.lineTo(0.0642, 0.4953)
loop_1 = loop_1.lineTo(0.053, 0.4258)
loop_1 = loop_1.threePointArc((0.05387, 0.44732), (0.0569, 0.46822))
loop_1 = loop_1.threePointArc((0.05757, 0.47412), (0.05845, 0.48008))
loop_1 = loop_1.threePointArc((0.06367, 0.49604), (0.06778, 0.50429))
loop_1 = loop_1.threePointArc((0.0791, 0.51663), (0.08781, 0.52455))
loop_1 = loop_1.lineTo(0.09808, 0.52925)
loop_1 = loop_1.threePointArc((0.11246, 0.53468), (0.126, 0.54017))
loop_1 = loop_1.threePointArc((0.1334, 0.5449), (0.13753, 0.54809))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_43_interval_0.stl')