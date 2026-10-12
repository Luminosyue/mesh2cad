import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.40048, -0.44895, -0.07659), normal=(-0.66585, 0.74608, -0.00024), xDir=(0.74608, 0.66585, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32971, -0.51156)
loop_1 = loop_1.lineTo(0.32058, -0.54721)
loop_1 = loop_1.lineTo(0.29231, -0.59149)
loop_1 = loop_1.lineTo(0.27588, -0.60418)
loop_1 = loop_1.lineTo(0.32963, -0.60713)
loop_1 = loop_1.lineTo(0.32971, -0.51305)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_42_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_42_interval_1.stl')