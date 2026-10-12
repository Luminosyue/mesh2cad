import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33899, 0.50463, 0.07744), normal=(-0.4301, 0.90277, 0.00412), xDir=(0.90278, 0.4301, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.89134, 0.42047)
loop_1 = loop_1.lineTo(0.9005, 0.40669)
loop_1 = loop_1.lineTo(0.89983, 0.36905)
loop_1 = loop_1.lineTo(0.89122, 0.35479)
loop_1 = loop_1.lineTo(0.88274, 0.36981)
loop_1 = loop_1.lineTo(0.88226, 0.40427)
loop_1 = loop_1.lineTo(0.88364, 0.41576)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/sketch_10_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/sketch_10_interval_1.stl')