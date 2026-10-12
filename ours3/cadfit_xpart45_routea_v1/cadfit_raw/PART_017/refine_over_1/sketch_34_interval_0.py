import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12533, -0.40605, 0.04968), normal=(0.00148, 1.0, -0.00071), xDir=(1.0, -0.00148, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41531, -0.70848)
loop_1 = loop_1.lineTo(0.39454, -0.71939)
loop_1 = loop_1.lineTo(0.37214, -0.73218)
loop_1 = loop_1.lineTo(0.35642, -0.74103)
loop_1 = loop_1.lineTo(0.33818, -0.74996)
loop_1 = loop_1.lineTo(0.44464, -0.75377)
loop_1 = loop_1.lineTo(0.44464, -0.69338)
loop_1 = loop_1.lineTo(0.41664, -0.70779)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_34_interval_0.stl')