import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04402, -0.19485, 0.55959), normal=(-0.00136, -0.00047, -1.0), xDir=(0.0, -1.0, 0.00047))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.61536, 0.89296)
loop_1 = loop_1.lineTo(-0.61536, 0.99459)
loop_1 = loop_1.lineTo(-0.20476, 0.99445)
loop_1 = loop_1.lineTo(-0.23708, 0.99245)
loop_1 = loop_1.lineTo(-0.28675, 0.98739)
loop_1 = loop_1.lineTo(-0.31395, 0.98174)
loop_1 = loop_1.lineTo(-0.33859, 0.97895)
loop_1 = loop_1.lineTo(-0.36575, 0.97334)
loop_1 = loop_1.lineTo(-0.39042, 0.96926)
loop_1 = loop_1.lineTo(-0.41754, 0.96193)
loop_1 = loop_1.lineTo(-0.43244, 0.95887)
loop_1 = loop_1.lineTo(-0.44701, 0.95587)
loop_1 = loop_1.threePointArc((-0.46681, 0.95036), (-0.48757, 0.94515))
loop_1 = loop_1.lineTo(-0.52112, 0.92965)
loop_1 = loop_1.lineTo(-0.54592, 0.92144)
loop_1 = loop_1.threePointArc((-0.56747, 0.9125), (-0.58542, 0.90558))
loop_1 = loop_1.lineTo(-0.61536, 0.89296)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_52_interval_0.stl')