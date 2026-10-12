import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69139, -0.06909, 0.05948), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.6212, 0.28876)
loop_1 = loop_1.lineTo(-0.67453, 0.24677)
loop_1 = loop_1.lineTo(-0.67564, 0.20948)
loop_1 = loop_1.lineTo(-0.68323, -0.20052)
loop_1 = loop_1.lineTo(0.70242, -0.20052)
loop_1 = loop_1.lineTo(0.6872, 0.20948)
loop_1 = loop_1.lineTo(0.63132, 0.20948)
loop_1 = loop_1.lineTo(0.629, 0.28627)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_24_interval_0.stl')