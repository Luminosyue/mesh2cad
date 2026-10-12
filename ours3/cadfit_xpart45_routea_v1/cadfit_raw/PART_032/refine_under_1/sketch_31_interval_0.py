import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03081, -0.71802, -0.1122), normal=(0.00089, 0.99996, 0.00894), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.09777, 0.14798)
loop_1 = loop_1.lineTo(-0.15749, 0.14798)
loop_1 = loop_1.lineTo(-0.14356, 0.05759)
loop_1 = loop_1.lineTo(-0.1236, 0.02791)
loop_1 = loop_1.lineTo(-0.10364, 0.09798)
loop_1 = loop_1.lineTo(-0.09796, 0.14642)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_31_interval_0.stl')