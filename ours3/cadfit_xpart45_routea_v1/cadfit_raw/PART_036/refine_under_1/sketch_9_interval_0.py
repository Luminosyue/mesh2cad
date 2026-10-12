import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.23226, -0.08678, -0.19882), normal=(0.02357, -0.65303, 0.75696), xDir=(-0.99935, -0.03607, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70322, -0.06171)
loop_1 = loop_1.lineTo(-0.71924, -0.07504)
loop_1 = loop_1.lineTo(-0.73911, -0.06992)
loop_1 = loop_1.lineTo(-0.74584, -0.03144)
loop_1 = loop_1.lineTo(-0.74611, -0.00549)
loop_1 = loop_1.lineTo(-0.7456, 0.01336)
loop_1 = loop_1.lineTo(-0.73083, 0.01605)
loop_1 = loop_1.lineTo(-0.70182, 0.01602)
loop_1 = loop_1.lineTo(-0.70184, -0.00405)
loop_1 = loop_1.threePointArc((-0.70139, -0.01486), (-0.70107, -0.02482))
loop_1 = loop_1.lineTo(-0.70063, -0.04584)
loop_1 = loop_1.threePointArc((-0.70071, -0.05281), (-0.70077, -0.05849))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_9_interval_0.stl')