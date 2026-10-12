import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01221, 0.42051)
loop_1 = loop_1.lineTo(-0.0042, 0.23277)
loop_1 = loop_1.lineTo(0.00422, 0.25562)
loop_1 = loop_1.lineTo(0.0042, 0.27227)
loop_1 = loop_1.lineTo(0.00362, 0.28478)
loop_1 = loop_1.threePointArc((0.00146, 0.30328), (-0.00089, 0.3209))
loop_1 = loop_1.threePointArc((-0.00223, 0.33067), (-0.0033, 0.34075))
loop_1 = loop_1.threePointArc((-0.00494, 0.35656), (-0.0063, 0.37293))
loop_1 = loop_1.lineTo(-0.00806, 0.38888)
loop_1 = loop_1.lineTo(-0.00905, 0.39977)
loop_1 = loop_1.threePointArc((-0.01065, 0.40992), (-0.01219, 0.42039))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_61_interval_0.stl')