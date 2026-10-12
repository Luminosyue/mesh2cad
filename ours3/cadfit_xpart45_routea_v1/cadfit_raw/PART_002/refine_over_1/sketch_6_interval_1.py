import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.30156, -0.30061, 0.34529), normal=(-0.14906, -0.98883, 2e-05), xDir=(-0.98883, 0.14906, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31067, 1.01062)
loop_1 = loop_1.lineTo(-0.3391, 0.99462)
loop_1 = loop_1.lineTo(-0.35349, 0.98614)
loop_1 = loop_1.lineTo(-0.37286, 0.97307)
loop_1 = loop_1.lineTo(-0.40327, 0.94912)
loop_1 = loop_1.lineTo(-0.4142, 0.93723)
loop_1 = loop_1.lineTo(-0.4142, 0.96515)
loop_1 = loop_1.lineTo(-0.31191, 1.01008)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_6_interval_1.stl')