import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.013, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.69145, -0.74663)
loop_1 = loop_1.lineTo(-0.70341, -0.72547)
loop_1 = loop_1.lineTo(-0.70334, -0.71061)
loop_1 = loop_1.lineTo(-0.70014, -0.7242)
loop_1 = loop_1.lineTo(-0.69182, -0.74532)
loop_1 = loop_1.lineTo(-0.72256, -0.64452)
loop_1 = loop_1.lineTo(-0.72088, -0.6548)
loop_1 = loop_1.threePointArc((-0.71793, -0.66628), (-0.71513, -0.67815))
loop_1 = loop_1.lineTo(-0.7091, -0.6949)
loop_1 = loop_1.lineTo(-0.72275, -0.66304)
loop_1 = loop_1.lineTo(-0.72244, -0.77)
loop_1 = loop_1.lineTo(-0.68007, -0.76989)
loop_1 = loop_1.lineTo(-0.69013, -0.75424)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_39_interval_0.stl')