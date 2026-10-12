import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.37603, 0.4236, 0.68306), normal=(0.52159, -0.00507, 0.85318), xDir=(-0.00972, -0.99995, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.54068, 0.17506)
loop_1 = loop_1.lineTo(-0.54036, 0.13686)
loop_1 = loop_1.lineTo(-0.53131, 0.15976)
loop_1 = loop_1.lineTo(-0.49124, 0.1682)
loop_1 = loop_1.threePointArc((-0.44678, 0.16868), (-0.41097, 0.16964))
loop_1 = loop_1.threePointArc((-0.36791, 0.17059), (-0.3307, 0.17088))
loop_1 = loop_1.lineTo(-0.29056, 0.1717)
loop_1 = loop_1.lineTo(-0.25514, 0.17038)
loop_1 = loop_1.lineTo(-0.21027, 0.17148)
loop_1 = loop_1.lineTo(-0.17012, 0.17067)
loop_1 = loop_1.lineTo(-0.12999, 0.17179)
loop_1 = loop_1.threePointArc((-0.08902, 0.17069), (-0.05625, 0.17057))
loop_1 = loop_1.threePointArc((-0.00873, 0.17045), (0.03058, 0.17146))
loop_1 = loop_1.lineTo(0.07073, 0.17109)
loop_1 = loop_1.lineTo(0.10015, 0.17284)
loop_1 = loop_1.lineTo(-0.53401, 0.17504)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_14_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_14_interval_1.stl')