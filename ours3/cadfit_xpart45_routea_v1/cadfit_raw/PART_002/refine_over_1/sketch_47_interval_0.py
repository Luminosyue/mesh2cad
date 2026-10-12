import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03108, -0.07617, 0.82), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14383, -0.52156)
loop_1 = loop_1.lineTo(0.14383, -0.64389)
loop_1 = loop_1.lineTo(0.0295, -0.64389)
loop_1 = loop_1.lineTo(0.04956, -0.63338)
loop_1 = loop_1.lineTo(0.07923, -0.61496)
loop_1 = loop_1.lineTo(0.09346, -0.60238)
loop_1 = loop_1.lineTo(0.11231, -0.57795)
loop_1 = loop_1.lineTo(0.12536, -0.55518)
loop_1 = loop_1.lineTo(0.1381, -0.53225)
loop_1 = loop_1.lineTo(0.14383, -0.52156)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_47_interval_0.stl')