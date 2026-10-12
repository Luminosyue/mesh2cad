import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.88116, -0.01891, 0.02861), normal=(0.99458, -0.104, 0.00154), xDir=(-0.104, -0.99458, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29146, 0.18433)
loop_1 = loop_1.lineTo(-0.29627, -0.20567)
loop_1 = loop_1.lineTo(0.2868, -0.20567)
loop_1 = loop_1.lineTo(0.2894, 0.18433)
loop_1 = loop_1.lineTo(-0.28254, 0.18433)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_30_interval_0.stl')