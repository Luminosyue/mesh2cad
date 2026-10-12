import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00755, -0.76431, 0.01109), normal=(0.00013, 0.99971, -0.02426), xDir=(1.0, -0.00013, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.54943, 0.25136)
loop_1 = loop_1.lineTo(0.46935, 0.25136)
loop_1 = loop_1.lineTo(0.48026, 0.24478)
loop_1 = loop_1.lineTo(0.49841, 0.22914)
loop_1 = loop_1.lineTo(0.52111, 0.20702)
loop_1 = loop_1.threePointArc((0.52706, 0.19679), (0.53213, 0.18767))
loop_1 = loop_1.lineTo(0.54693, 0.15887)
loop_1 = loop_1.lineTo(0.5498, 0.12467)
loop_1 = loop_1.lineTo(0.552, 0.18702)
loop_1 = loop_1.lineTo(0.53869, 0.18702)
loop_1 = loop_1.lineTo(0.54912, 0.24947)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_13_interval_0.stl')