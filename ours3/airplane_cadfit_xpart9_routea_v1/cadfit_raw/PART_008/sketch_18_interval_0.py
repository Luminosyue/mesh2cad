import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94258, -0.13621)
loop_1 = loop_1.lineTo(0.95674, -0.13543)
loop_1 = loop_1.lineTo(0.96856, -0.1219)
loop_1 = loop_1.lineTo(0.97905, -0.10386)
loop_1 = loop_1.lineTo(0.99265, -0.0867)
loop_1 = loop_1.lineTo(0.99349, -0.06786)
loop_1 = loop_1.lineTo(0.98255, -0.04765)
loop_1 = loop_1.lineTo(0.97604, -0.03225)
loop_1 = loop_1.lineTo(0.95654, -0.02533)
loop_1 = loop_1.lineTo(0.95161, -0.03779)
loop_1 = loop_1.lineTo(0.95556, -0.05121)
loop_1 = loop_1.lineTo(0.96189, -0.06871)
loop_1 = loop_1.lineTo(0.96282, -0.08175)
loop_1 = loop_1.lineTo(0.95824, -0.10293)
loop_1 = loop_1.lineTo(0.9503, -0.12275)
loop_1 = loop_1.lineTo(0.94263, -0.13613)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_008/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_008/sketch_18_interval_0.stl')