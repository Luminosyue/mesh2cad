import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.68376, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06333, 0.84)
loop_1 = loop_1.lineTo(0.06274, 0.50252)
loop_1 = loop_1.lineTo(0.05204, 0.53948)
loop_1 = loop_1.lineTo(0.04943, 0.54968)
loop_1 = loop_1.lineTo(0.04759, 0.57429)
loop_1 = loop_1.threePointArc((0.04627, 0.60362), (0.0447, 0.63154))
loop_1 = loop_1.lineTo(0.04398, 0.65377)
loop_1 = loop_1.lineTo(0.0447, 0.71713)
loop_1 = loop_1.lineTo(0.04667, 0.84)
loop_1 = loop_1.lineTo(0.06309, 0.84)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_25_interval_0.stl')