import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00232, 0.44459, -0.11481), normal=(-0.0, -0.73449, -0.67862), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24147, 0.17874)
loop_1 = loop_1.lineTo(0.22079, 0.18379)
loop_1 = loop_1.lineTo(0.08002, 0.20168)
loop_1 = loop_1.lineTo(0.01462, 0.21165)
loop_1 = loop_1.lineTo(-0.07916, 0.19068)
loop_1 = loop_1.lineTo(-0.11545, 0.19122)
loop_1 = loop_1.lineTo(-0.17292, 0.18795)
loop_1 = loop_1.lineTo(-0.19539, 0.17874)
loop_1 = loop_1.lineTo(0.23679, 0.17874)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_25_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_25_interval_1.stl')