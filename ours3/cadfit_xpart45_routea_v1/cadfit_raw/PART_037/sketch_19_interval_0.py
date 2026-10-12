import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45951, 0.08656, 0.27458), normal=(-0.00174, 0.42485, -0.90526), xDir=(0.0, -0.90526, -0.42485))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28769, -0.08915)
loop_1 = loop_1.lineTo(0.28699, -0.10125)
loop_1 = loop_1.lineTo(0.27981, -0.11781)
loop_1 = loop_1.lineTo(0.26938, -0.12887)
loop_1 = loop_1.lineTo(0.25669, -0.13776)
loop_1 = loop_1.threePointArc((0.24467, -0.14209), (0.23941, -0.1432))
loop_1 = loop_1.threePointArc((0.23096, -0.1418), (0.22434, -0.14077))
loop_1 = loop_1.lineTo(0.2036, -0.12657)
loop_1 = loop_1.lineTo(0.1905, -0.10279)
loop_1 = loop_1.lineTo(0.19186, -0.08915)
loop_1 = loop_1.lineTo(0.21554, -0.06204)
loop_1 = loop_1.threePointArc((0.23198, -0.05325), (0.23933, -0.04994))
loop_1 = loop_1.threePointArc((0.24606, -0.05007), (0.25144, -0.05016))
loop_1 = loop_1.lineTo(0.26948, -0.05916)
loop_1 = loop_1.lineTo(0.28408, -0.07525)
loop_1 = loop_1.lineTo(0.28737, -0.08784)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_19_interval_0.stl')