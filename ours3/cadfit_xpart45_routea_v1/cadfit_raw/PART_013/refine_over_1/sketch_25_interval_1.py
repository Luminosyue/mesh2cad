import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2026, -0.82889, 0.05883), normal=(-0.0002, -0.99988, 0.01551), xDir=(-1.0, 0.0002, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28918, 0.21738)
loop_1 = loop_1.lineTo(-0.2659, 0.23641)
loop_1 = loop_1.lineTo(-0.32654, 0.06972)
loop_1 = loop_1.lineTo(-0.32599, 0.09697)
loop_1 = loop_1.lineTo(-0.32034, 0.16315)
loop_1 = loop_1.lineTo(-0.30847, 0.18381)
loop_1 = loop_1.lineTo(-0.30095, 0.19826)
loop_1 = loop_1.lineTo(-0.28918, 0.21738)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_25_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_25_interval_1.stl')