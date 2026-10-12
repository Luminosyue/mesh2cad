import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.04229), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21103, -0.99088)
loop_1 = loop_1.lineTo(-0.10672, -0.99035)
loop_1 = loop_1.lineTo(-0.10769, -0.76209)
loop_1 = loop_1.threePointArc((-0.10969, -0.78444), (-0.11005, -0.80518))
loop_1 = loop_1.threePointArc((-0.10985, -0.8242), (-0.10956, -0.84225))
loop_1 = loop_1.lineTo(-0.10878, -0.86607)
loop_1 = loop_1.lineTo(-0.10881, -0.90104)
loop_1 = loop_1.threePointArc((-0.10957, -0.91198), (-0.11086, -0.92312))
loop_1 = loop_1.threePointArc((-0.11186, -0.93262), (-0.11346, -0.94222))
loop_1 = loop_1.lineTo(-0.13844, -0.9743)
loop_1 = loop_1.lineTo(-0.14995, -0.9845)
loop_1 = loop_1.threePointArc((-0.16838, -0.98734), (-0.18762, -0.98997))
loop_1 = loop_1.lineTo(-0.21083, -0.99088)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_49_interval_0.stl')