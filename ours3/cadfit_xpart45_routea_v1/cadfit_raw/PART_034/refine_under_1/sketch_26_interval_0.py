import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.77678, 0.31669, 0.07023), normal=(0.8984, -0.43914, 0.00575), xDir=(-0.43915, -0.89841, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31375, 0.22613)
loop_1 = loop_1.lineTo(-0.31668, -0.16388)
loop_1 = loop_1.lineTo(0.34042, -0.16388)
loop_1 = loop_1.lineTo(0.34364, 0.22613)
loop_1 = loop_1.lineTo(-0.30722, 0.22613)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_26_interval_0.stl')