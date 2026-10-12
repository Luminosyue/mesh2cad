import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.14136, -0.01672, 0.00933), normal=(-0.99992, 0.0086, 0.00942), xDir=(0.0086, 0.99996, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23793, 0.00983)
loop_1 = loop_1.lineTo(0.23881, -0.00871)
loop_1 = loop_1.lineTo(0.17913, -0.03036)
loop_1 = loop_1.lineTo(0.12666, -0.03556)
loop_1 = loop_1.threePointArc((0.13572, -0.0322), (0.14523, -0.0289))
loop_1 = loop_1.lineTo(0.16426, -0.02095)
loop_1 = loop_1.lineTo(0.18131, -0.0141)
loop_1 = loop_1.lineTo(0.19262, -0.0101)
loop_1 = loop_1.lineTo(0.20939, -0.00243)
loop_1 = loop_1.threePointArc((0.21659, 0.0006), (0.22347, 0.0036))
loop_1 = loop_1.lineTo(0.23793, 0.00983)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_5_interval_0.stl')