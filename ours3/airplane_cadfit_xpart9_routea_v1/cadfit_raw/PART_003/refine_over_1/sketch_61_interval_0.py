import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.04075), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02015, 0.97221)
loop_1 = loop_1.lineTo(0.0203, 0.92278)
loop_1 = loop_1.lineTo(0.05349, 0.95128)
loop_1 = loop_1.threePointArc((0.06773, 0.9578), (0.07683, 0.96094))
loop_1 = loop_1.lineTo(0.09373, 0.96759)
loop_1 = loop_1.lineTo(0.11956, 0.97064)
loop_1 = loop_1.lineTo(0.02024, 0.97221)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_61_interval_0.stl')