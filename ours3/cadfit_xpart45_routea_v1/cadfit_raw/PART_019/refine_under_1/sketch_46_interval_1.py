import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45169, -0.11753, -0.29507), normal=(0.83379, 0.00102, 0.55208), xDir=(0.00123, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70386, -0.31357)
loop_1 = loop_1.lineTo(-0.83774, -0.3139)
loop_1 = loop_1.lineTo(-0.81632, -0.32985)
loop_1 = loop_1.lineTo(-0.75546, -0.32457)
loop_1 = loop_1.lineTo(-0.70519, -0.31385)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_46_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_46_interval_1.stl')