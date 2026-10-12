import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.54386, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.10635, 0.31595)
loop_1 = loop_1.threePointArc((-0.10714, 0.31002), (-0.1082, 0.30388))
loop_1 = loop_1.lineTo(-0.11151, 0.28308)
loop_1 = loop_1.lineTo(-0.10348, 0.24751)
loop_1 = loop_1.threePointArc((-0.09541, 0.22741), (-0.08759, 0.20823))
loop_1 = loop_1.lineTo(-0.15285, 0.25656)
loop_1 = loop_1.lineTo(-0.1064, 0.31588)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_44_interval_0.stl')