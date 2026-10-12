import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59865, 0.56995, 0.0314), normal=(0.73909, -0.67356, 0.00868), xDir=(-0.67358, -0.73911, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34434, -0.2026)
loop_1 = loop_1.lineTo(-0.40871, -0.2026)
loop_1 = loop_1.lineTo(-0.40791, 0.18741)
loop_1 = loop_1.lineTo(0.34803, 0.18741)
loop_1 = loop_1.lineTo(0.34445, -0.19179)
loop_1 = loop_1.lineTo(0.34434, -0.2026)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_40_interval_0.stl')