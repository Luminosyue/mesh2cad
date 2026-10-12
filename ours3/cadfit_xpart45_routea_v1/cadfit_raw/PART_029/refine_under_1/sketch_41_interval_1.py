import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08809, -0.11256)
loop_1 = loop_1.lineTo(0.09859, -0.05558)
loop_1 = loop_1.lineTo(0.10139, 0.01)
loop_1 = loop_1.lineTo(-0.05396, 0.00953)
loop_1 = loop_1.lineTo(-0.06135, -0.14)
loop_1 = loop_1.lineTo(-0.02647, -0.13975)
loop_1 = loop_1.threePointArc((-0.01762, -0.14208), (-0.0128, -0.14649))
loop_1 = loop_1.lineTo(0.0879, -0.11263)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_41_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_41_interval_1.stl')