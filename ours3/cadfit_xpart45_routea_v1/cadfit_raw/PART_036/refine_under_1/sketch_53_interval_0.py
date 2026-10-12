import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.14678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2296, 0.09115)
loop_1 = loop_1.lineTo(-0.23992, 0.0779)
loop_1 = loop_1.lineTo(-0.27647, 0.0769)
loop_1 = loop_1.lineTo(-0.27708, 0.08905)
loop_1 = loop_1.lineTo(-0.27831, 0.07329)
loop_1 = loop_1.lineTo(-0.27778, 0.05629)
loop_1 = loop_1.lineTo(-0.27018, 0.03901)
loop_1 = loop_1.lineTo(-0.25101, 0.0331)
loop_1 = loop_1.lineTo(-0.23982, 0.03933)
loop_1 = loop_1.lineTo(-0.23039, 0.05678)
loop_1 = loop_1.lineTo(-0.229, 0.07454)
loop_1 = loop_1.lineTo(-0.2296, 0.09109)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_53_interval_0.stl')