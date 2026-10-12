import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2397, -0.11873, -0.19406), normal=(0.07595, 0.98701, -0.14157), xDir=(0.99705, -0.07672, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.15899, -0.25333)
loop_1 = loop_1.lineTo(-1.22173, -0.25333)
loop_1 = loop_1.lineTo(-1.23178, -0.32682)
loop_1 = loop_1.lineTo(-1.23917, -0.38409)
loop_1 = loop_1.lineTo(-1.15947, -0.2563)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-1.20108, -0.31004)
loop_2 = loop_2.lineTo(-1.19096, -0.29461)
loop_2 = loop_2.lineTo(-1.1832, -0.28253)
loop_2 = loop_2.lineTo(-1.15852, -0.25479)
loop_2 = loop_2.lineTo(-1.22173, -0.25333)
loop_2 = loop_2.lineTo(-1.23178, -0.32682)
loop_2 = loop_2.lineTo(-1.23917, -0.38409)
loop_2 = loop_2.lineTo(-1.20189, -0.31161)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_5_interval_0.stl')