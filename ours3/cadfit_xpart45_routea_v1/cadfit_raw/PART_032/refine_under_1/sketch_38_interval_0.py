import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00232, 0.84855, 0.25843), normal=(-0.0, -0.73449, -0.67862), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26069, 0.11684)
loop_1 = loop_1.threePointArc((0.24076, 0.12416), (0.22144, 0.13066))
loop_1 = loop_1.threePointArc((0.19505, 0.13968), (0.17367, 0.14621))
loop_1 = loop_1.lineTo(0.15462, 0.15225)
loop_1 = loop_1.threePointArc((0.12639, 0.16702), (0.10377, 0.17798))
loop_1 = loop_1.lineTo(0.06162, 0.19873)
loop_1 = loop_1.lineTo(-0.00935, 0.18302)
loop_1 = loop_1.lineTo(-0.03218, 0.17705)
loop_1 = loop_1.lineTo(-0.07512, 0.16327)
loop_1 = loop_1.threePointArc((-0.11161, 0.15272), (-0.14542, 0.14393))
loop_1 = loop_1.lineTo(-0.1728, 0.13723)
loop_1 = loop_1.lineTo(-0.20306, 0.12386)
loop_1 = loop_1.lineTo(-0.21659, 0.11704)
loop_1 = loop_1.lineTo(0.25648, 0.11684)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_38_interval_0.stl')