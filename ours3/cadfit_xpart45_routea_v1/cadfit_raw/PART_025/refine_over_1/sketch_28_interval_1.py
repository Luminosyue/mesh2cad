import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.85887, -0.26145, -0.00978), normal=(-0.99977, 0.02155, 1e-05), xDir=(0.02155, 0.99977, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32967, 0.13899)
loop_1 = loop_1.lineTo(0.32899, 0.12173)
loop_1 = loop_1.lineTo(0.32543, 0.10528)
loop_1 = loop_1.lineTo(0.30005, 0.1038)
loop_1 = loop_1.lineTo(0.29869, 0.11442)
loop_1 = loop_1.lineTo(0.32967, 0.13899)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_28_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_28_interval_1.stl')