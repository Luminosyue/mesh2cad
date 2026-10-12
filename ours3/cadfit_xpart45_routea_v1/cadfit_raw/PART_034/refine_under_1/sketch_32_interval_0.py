import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.89804, -0.01606, 0.01005), normal=(0.99411, -0.10841, -0.0005), xDir=(-0.10841, -0.99411, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20724, 0.16569)
loop_1 = loop_1.lineTo(-0.21594, -0.22431)
loop_1 = loop_1.lineTo(0.19714, -0.22431)
loop_1 = loop_1.lineTo(0.19485, 0.16569)
loop_1 = loop_1.lineTo(-0.19895, 0.16569)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_32_interval_0.stl')