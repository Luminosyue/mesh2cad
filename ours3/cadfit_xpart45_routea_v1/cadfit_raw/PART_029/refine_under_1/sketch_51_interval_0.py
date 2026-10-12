import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.13, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.20931, -0.1411)
loop_1 = loop_1.circle(0.02914)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_51_interval_0.stl')