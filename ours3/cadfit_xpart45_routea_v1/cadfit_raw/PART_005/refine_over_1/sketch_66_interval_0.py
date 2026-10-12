import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32007, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.9986, 0.20306)
loop_1 = loop_1.lineTo(0.99698, -0.53018)
loop_1 = loop_1.lineTo(0.98426, -0.53018)
loop_1 = loop_1.threePointArc((0.99014, -0.49093), (0.99015, -0.46199))
loop_1 = loop_1.threePointArc((0.98797, -0.41072), (0.9873, -0.35781))
loop_1 = loop_1.threePointArc((0.98518, -0.30324), (0.98462, -0.24691))
loop_1 = loop_1.threePointArc((0.98411, -0.20321), (0.98599, -0.15827))
loop_1 = loop_1.lineTo(0.97793, -0.10666)
loop_1 = loop_1.threePointArc((0.96129, -0.08749), (0.94509, -0.06728))
loop_1 = loop_1.threePointArc((0.93371, -0.06152), (0.92278, -0.05527))
loop_1 = loop_1.lineTo(0.9037, -0.02131)
loop_1 = loop_1.lineTo(0.89568, -0.00376)
loop_1 = loop_1.threePointArc((0.9223, 0.01701), (0.94709, 0.03712))
loop_1 = loop_1.lineTo(0.95698, 0.04946)
loop_1 = loop_1.lineTo(0.9833, 0.10241)
loop_1 = loop_1.threePointArc((0.98982, 0.12759), (0.99701, 0.15317))
loop_1 = loop_1.threePointArc((0.9975, 0.17767), (0.9986, 0.20254))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_66_interval_0.stl')