import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.00092), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03507, -0.24862)
loop_1 = loop_1.lineTo(0.03709, -0.26108)
loop_1 = loop_1.lineTo(0.03969, -0.27257)
loop_1 = loop_1.threePointArc((0.04069, -0.27851), (0.0418, -0.2841))
loop_1 = loop_1.lineTo(0.04322, -0.30697)
loop_1 = loop_1.threePointArc((0.04305, -0.31247), (0.04263, -0.31818))
loop_1 = loop_1.lineTo(0.07611, -0.3184)
loop_1 = loop_1.lineTo(0.07548, -0.30799)
loop_1 = loop_1.lineTo(0.07165, -0.28837)
loop_1 = loop_1.lineTo(0.0541, -0.26017)
loop_1 = loop_1.lineTo(0.02683, -0.23529)
loop_1 = loop_1.lineTo(0.03507, -0.24862)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_68_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_68_interval_0.stl')