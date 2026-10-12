import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03082, -0.70802, -0.11212), normal=(0.00089, 0.99996, 0.00894), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06797, -0.25637)
loop_1 = loop_1.lineTo(0.04793, 0.12667)
loop_1 = loop_1.lineTo(0.04635, 0.14798)
loop_1 = loop_1.lineTo(0.16006, 0.14798)
loop_1 = loop_1.lineTo(0.15159, -0.25634)
loop_1 = loop_1.lineTo(0.06799, -0.25637)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_5_interval_0.stl')