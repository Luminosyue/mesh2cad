import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.88427, -0.22518, 0.12854), normal=(0.98989, -0.14162, -0.00737), xDir=(-0.14163, -0.98992, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27571, 0.62912)
loop_1 = loop_1.lineTo(-0.27454, 0.68481)
loop_1 = loop_1.lineTo(-0.24777, 0.68477)
loop_1 = loop_1.lineTo(-0.25542, 0.67072)
loop_1 = loop_1.lineTo(-0.27926, 0.48053)
loop_1 = loop_1.lineTo(-0.28137, 0.51571)
loop_1 = loop_1.lineTo(-0.28362, 0.53033)
loop_1 = loop_1.lineTo(-0.28223, 0.56551)
loop_1 = loop_1.lineTo(-0.28219, 0.58013)
loop_1 = loop_1.lineTo(-0.27806, 0.61594)
loop_1 = loop_1.lineTo(-0.2761, 0.62693)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_30_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_30_interval_1.stl')