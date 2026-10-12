import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.891, 0.00578, -0.00094), normal=(-0.73951, 0.67314, 0.00309), xDir=(0.67314, 0.73952, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2607, 0.06923)
loop_1 = loop_1.lineTo(-0.26029, 0.03528)
loop_1 = loop_1.lineTo(0.04523, 0.03506)
loop_1 = loop_1.lineTo(-0.25937, -0.091)
loop_1 = loop_1.lineTo(-0.26069, -0.07662)
loop_1 = loop_1.lineTo(-0.2604, -0.05848)
loop_1 = loop_1.lineTo(-0.26121, -0.03969)
loop_1 = loop_1.lineTo(-0.26311, -0.00418)
loop_1 = loop_1.lineTo(-0.26273, 0.00745)
loop_1 = loop_1.threePointArc((-0.26279, 0.02096), (-0.26301, 0.03159))
loop_1 = loop_1.lineTo(-0.2607, 0.06923)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_6_interval_0.stl')