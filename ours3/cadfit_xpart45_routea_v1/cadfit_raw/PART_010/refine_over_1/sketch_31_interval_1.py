import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64063, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.13172, -0.61308)
loop_1 = loop_1.lineTo(-0.14204, -0.60858)
loop_1 = loop_1.lineTo(-0.16849, -0.61663)
loop_1 = loop_1.lineTo(-0.17871, -0.61512)
loop_1 = loop_1.lineTo(-0.18878, -0.61676)
loop_1 = loop_1.lineTo(-0.20117, -0.62402)
loop_1 = loop_1.lineTo(-0.21155, -0.63396)
loop_1 = loop_1.lineTo(-0.24118, -0.66422)
loop_1 = loop_1.lineTo(-0.12672, -0.66761)
loop_1 = loop_1.lineTo(-0.12694, -0.61441)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_31_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_31_interval_1.stl')