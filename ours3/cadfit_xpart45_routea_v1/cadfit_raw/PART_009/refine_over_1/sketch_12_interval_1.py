import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.82029, 0.34684, 0.16743), normal=(-0.91532, 0.40273, -0.0), xDir=(0.40273, 0.91532, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16685, 0.09514)
loop_1 = loop_1.lineTo(0.19984, 0.09984)
loop_1 = loop_1.lineTo(0.24276, 0.0849)
loop_1 = loop_1.lineTo(0.24232, 0.20503)
loop_1 = loop_1.lineTo(0.16893, 0.09816)
loop_1 = loop_1.lineTo(0.14961, 0.10047)
loop_1 = loop_1.lineTo(0.16685, 0.09514)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_12_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_12_interval_1.stl')