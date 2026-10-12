import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.40731, -0.03128, -0.00197), normal=(-0.96875, 0.24802, -0.00174), xDir=(0.24802, 0.96876, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28803, -0.32475)
loop_1 = loop_1.lineTo(-0.28853, -0.59666)
loop_1 = loop_1.lineTo(-0.30245, -0.57267)
loop_1 = loop_1.lineTo(-0.32005, -0.54945)
loop_1 = loop_1.lineTo(-0.31858, -0.52418)
loop_1 = loop_1.lineTo(-0.30297, -0.49589)
loop_1 = loop_1.lineTo(-0.29636, -0.47697)
loop_1 = loop_1.threePointArc((-0.2915, -0.45594), (-0.29086, -0.44499))
loop_1 = loop_1.threePointArc((-0.29044, -0.4201), (-0.29031, -0.39903))
loop_1 = loop_1.lineTo(-0.28875, -0.36795)
loop_1 = loop_1.threePointArc((-0.28855, -0.34677), (-0.2881, -0.32772))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_33_interval_0.stl')