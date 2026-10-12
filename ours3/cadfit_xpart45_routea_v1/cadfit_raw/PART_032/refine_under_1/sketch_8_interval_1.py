import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03082, -0.70802, -0.11212), normal=(0.00089, 0.99996, 0.00894), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.002, -0.21308)
loop_1 = loop_1.lineTo(0.00365, -0.19978)
loop_1 = loop_1.lineTo(0.01269, -0.17971)
loop_1 = loop_1.lineTo(0.0266, -0.1838)
loop_1 = loop_1.lineTo(0.0183, -0.17086)
loop_1 = loop_1.lineTo(0.16506, -0.17086)
loop_1 = loop_1.lineTo(0.16218, -0.21203)
loop_1 = loop_1.lineTo(-0.00156, -0.21203)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_8_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_8_interval_1.stl')