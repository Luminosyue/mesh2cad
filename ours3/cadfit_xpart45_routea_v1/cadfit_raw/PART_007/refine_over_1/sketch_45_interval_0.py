import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.24245, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.99, -0.53792)
loop_1 = loop_1.lineTo(0.98984, -0.60646)
loop_1 = loop_1.lineTo(0.92321, -0.60633)
loop_1 = loop_1.lineTo(0.94939, -0.58883)
loop_1 = loop_1.lineTo(0.9662, -0.57781)
loop_1 = loop_1.lineTo(0.97826, -0.55878)
loop_1 = loop_1.lineTo(0.98996, -0.53798)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_45_interval_0.stl')