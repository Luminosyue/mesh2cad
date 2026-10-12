import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.39939, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22, 0.97169)
loop_1 = loop_1.lineTo(0.21973, 0.88773)
loop_1 = loop_1.lineTo(0.21169, 0.90034)
loop_1 = loop_1.threePointArc((0.19004, 0.91738), (0.17526, 0.92791))
loop_1 = loop_1.threePointArc((0.15801, 0.93832), (0.1492, 0.94267))
loop_1 = loop_1.threePointArc((0.13041, 0.95198), (0.11233, 0.96054))
loop_1 = loop_1.lineTo(0.09283, 0.96897)
loop_1 = loop_1.lineTo(0.08209, 0.97169)
loop_1 = loop_1.lineTo(0.21987, 0.97169)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_70_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_70_interval_0.stl')