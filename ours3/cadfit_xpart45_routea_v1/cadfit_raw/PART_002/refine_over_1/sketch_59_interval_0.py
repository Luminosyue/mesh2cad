import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.37885, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36212, 0.77)
loop_1 = loop_1.lineTo(0.3619, 0.65047)
loop_1 = loop_1.lineTo(0.35325, 0.67918)
loop_1 = loop_1.lineTo(0.33919, 0.71516)
loop_1 = loop_1.lineTo(0.32471, 0.74911)
loop_1 = loop_1.threePointArc((0.31987, 0.75938), (0.31494, 0.77001))
loop_1 = loop_1.lineTo(0.36202, 0.77)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_59_interval_0.stl')