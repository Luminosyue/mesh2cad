import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.1, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03959, -0.05161)
loop_1 = loop_1.lineTo(0.02489, -0.05436)
loop_1 = loop_1.lineTo(0.00509, -0.06194)
loop_1 = loop_1.lineTo(-0.01312, -0.07902)
loop_1 = loop_1.lineTo(-0.02101, -0.09881)
loop_1 = loop_1.threePointArc((-0.02069, -0.11379), (-0.01912, -0.12328))
loop_1 = loop_1.lineTo(-0.0026, -0.14302)
loop_1 = loop_1.lineTo(0.02028, -0.15377)
loop_1 = loop_1.lineTo(0.03979, -0.15355)
loop_1 = loop_1.lineTo(0.05947, -0.14526)
loop_1 = loop_1.lineTo(0.07905, -0.12599)
loop_1 = loop_1.lineTo(0.0878, -0.10334)
loop_1 = loop_1.threePointArc((0.08715, -0.09605), (0.08674, -0.08856))
loop_1 = loop_1.lineTo(0.07826, -0.07038)
loop_1 = loop_1.lineTo(0.05879, -0.05614)
loop_1 = loop_1.lineTo(0.04435, -0.05317)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_6_interval_0.stl')