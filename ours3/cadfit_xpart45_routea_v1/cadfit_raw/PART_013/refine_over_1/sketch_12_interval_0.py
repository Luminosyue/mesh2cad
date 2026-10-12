import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.78635, 0.64903, 0.00292), normal=(-0.98947, 0.14472, 0.00218), xDir=(0.14472, 0.98947, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.62824, 0.19438)
loop_1 = loop_1.lineTo(-1.0329, 0.20944)
loop_1 = loop_1.lineTo(-1.02158, 0.21054)
loop_1 = loop_1.lineTo(-1.61165, 0.21054)
loop_1 = loop_1.lineTo(-1.61274, 0.20038)
loop_1 = loop_1.lineTo(-1.62308, 0.19638)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_12_interval_0.stl')