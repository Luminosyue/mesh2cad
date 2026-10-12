import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00978, 0.00728, -0.23261), normal=(-0.00713, -0.03239, 0.99945), xDir=(-0.0, 0.99948, 0.03239))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.40709, 0.52177)
loop_1 = loop_1.lineTo(0.5898, 0.52177)
loop_1 = loop_1.lineTo(0.58395, 0.5372)
loop_1 = loop_1.lineTo(0.54958, 0.56159)
loop_1 = loop_1.lineTo(0.52042, 0.55734)
loop_1 = loop_1.lineTo(0.50026, 0.57267)
loop_1 = loop_1.lineTo(0.47938, 0.56562)
loop_1 = loop_1.lineTo(0.45096, 0.54867)
loop_1 = loop_1.lineTo(0.42814, 0.5372)
loop_1 = loop_1.lineTo(0.40865, 0.52291)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_6_interval_0.stl')