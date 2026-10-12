import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.20741), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06951, 0.27159)
loop_1 = loop_1.threePointArc((0.07512, 0.27151), (0.08096, 0.27125))
loop_1 = loop_1.lineTo(0.1218, 0.27004)
loop_1 = loop_1.lineTo(0.13404, 0.15538)
loop_1 = loop_1.lineTo(0.13551, 0.11718)
loop_1 = loop_1.lineTo(0.09357, 0.11485)
loop_1 = loop_1.threePointArc((0.08203, 0.11408), (0.07547, 0.11418))
loop_1 = loop_1.lineTo(0.06556, 0.26962)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_66_interval_0.stl')