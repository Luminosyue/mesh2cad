import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03621, 0.12831, -0.2158), normal=(0.01246, -0.99992, -0.00166), xDir=(-0.99992, -0.01246, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35737, -0.51539)
loop_1 = loop_1.lineTo(-0.3339, -0.54094)
loop_1 = loop_1.lineTo(-0.30126, -0.57538)
loop_1 = loop_1.lineTo(-0.29668, -0.59328)
loop_1 = loop_1.lineTo(-0.29176, -0.61032)
loop_1 = loop_1.threePointArc((-0.29061, -0.62864), (-0.28981, -0.64526))
loop_1 = loop_1.threePointArc((-0.29019, -0.66552), (-0.29045, -0.68427))
loop_1 = loop_1.lineTo(-0.36393, -0.50871)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_13_interval_0.stl')