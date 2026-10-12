import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.70063, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28166, 0.76428)
loop_1 = loop_1.lineTo(0.11109, 0.76441)
loop_1 = loop_1.lineTo(0.11123, 0.69418)
loop_1 = loop_1.lineTo(0.13356, 0.69376)
loop_1 = loop_1.lineTo(0.15056, 0.6931)
loop_1 = loop_1.threePointArc((0.16191, 0.69611), (0.17252, 0.69948))
loop_1 = loop_1.threePointArc((0.1805, 0.70204), (0.18795, 0.70465))
loop_1 = loop_1.lineTo(0.21371, 0.72514)
loop_1 = loop_1.lineTo(0.23789, 0.74289)
loop_1 = loop_1.lineTo(0.26075, 0.75832)
loop_1 = loop_1.lineTo(0.28152, 0.76425)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_30_interval_0.stl')