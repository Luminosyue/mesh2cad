import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00737, 0.61528, -0.02238), normal=(0.00013, 0.99971, -0.02426), xDir=(1.0, -0.00013, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.54943, -0.18115)
loop_1 = loop_1.lineTo(0.54943, -0.25784)
loop_1 = loop_1.lineTo(0.46933, -0.25782)
loop_1 = loop_1.lineTo(0.48026, -0.24656)
loop_1 = loop_1.lineTo(0.49761, -0.22638)
loop_1 = loop_1.lineTo(0.50819, -0.21763)
loop_1 = loop_1.lineTo(0.52162, -0.20864)
loop_1 = loop_1.lineTo(0.54845, -0.18213)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_17_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_17_interval_1.stl')