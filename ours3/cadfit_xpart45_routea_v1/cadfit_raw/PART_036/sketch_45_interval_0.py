import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.19741), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14939, -0.95103)
loop_1 = loop_1.lineTo(0.15704, -0.96857)
loop_1 = loop_1.lineTo(0.17842, -0.9839)
loop_1 = loop_1.lineTo(0.1962, -0.98571)
loop_1 = loop_1.lineTo(0.2136, -0.9793)
loop_1 = loop_1.lineTo(0.22451, -0.9683)
loop_1 = loop_1.lineTo(0.23171, -0.95159)
loop_1 = loop_1.threePointArc((0.23097, -0.94174), (0.23003, -0.93347))
loop_1 = loop_1.lineTo(0.21781, -0.91598)
loop_1 = loop_1.lineTo(0.1962, -0.90875)
loop_1 = loop_1.lineTo(0.17796, -0.9124)
loop_1 = loop_1.lineTo(0.16143, -0.92347)
loop_1 = loop_1.lineTo(0.15277, -0.93377)
loop_1 = loop_1.lineTo(0.14945, -0.9507)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_45_interval_0.stl')