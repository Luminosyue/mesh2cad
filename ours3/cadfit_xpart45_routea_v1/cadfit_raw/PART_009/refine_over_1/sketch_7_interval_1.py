import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47457, -0.75015, 0.26835), normal=(0.55903, -0.82914, -0.00126), xDir=(-0.82914, -0.55903, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07884, 0.2051)
loop_1 = loop_1.lineTo(0.00242, 0.20594)
loop_1 = loop_1.lineTo(-0.21547, 0.3438)
loop_1 = loop_1.lineTo(-0.21748, 0.18637)
loop_1 = loop_1.lineTo(-0.20671, 0.18977)
loop_1 = loop_1.lineTo(-0.1836, 0.19796)
loop_1 = loop_1.lineTo(-0.14819, 0.19887)
loop_1 = loop_1.lineTo(-0.09021, 0.20618)
loop_1 = loop_1.lineTo(-0.07494, 0.20655)
loop_1 = loop_1.lineTo(-0.0223, 0.20425)
loop_1 = loop_1.lineTo(-0.00178, 0.20566)
loop_1 = loop_1.lineTo(0.03993, 0.20411)
loop_1 = loop_1.lineTo(0.07495, 0.205)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_7_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_7_interval_1.stl')