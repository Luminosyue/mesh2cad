import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.36141, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0677, 0.8)
loop_1 = loop_1.lineTo(0.20668, 0.79966)
loop_1 = loop_1.lineTo(0.1874, 0.78311)
loop_1 = loop_1.lineTo(0.16287, 0.77489)
loop_1 = loop_1.lineTo(0.15256, 0.76951)
loop_1 = loop_1.lineTo(0.12825, 0.77688)
loop_1 = loop_1.lineTo(0.11764, 0.77538)
loop_1 = loop_1.lineTo(0.09843, 0.7862)
loop_1 = loop_1.lineTo(0.0859, 0.78849)
loop_1 = loop_1.lineTo(0.06987, 0.79406)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_35_interval_0.stl')