import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.09041), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11, -0.03065)
loop_1 = loop_1.lineTo(-0.06699, -0.34406)
loop_1 = loop_1.lineTo(-0.09138, -0.47652)
loop_1 = loop_1.threePointArc((-0.09589, -0.50257), (-0.10105, -0.52921))
loop_1 = loop_1.threePointArc((-0.10501, -0.55506), (-0.10974, -0.58148))
loop_1 = loop_1.lineTo(-0.11, -0.03102)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_54_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_54_interval_1.stl')