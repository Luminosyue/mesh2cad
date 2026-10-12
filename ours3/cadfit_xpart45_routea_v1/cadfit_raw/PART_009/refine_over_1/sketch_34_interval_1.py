import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.87809, 0.07585, 0.00942), normal=(0.9762, 0.21686, 0.00033), xDir=(0.21686, -0.9762, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02206, -0.05682)
loop_1 = loop_1.lineTo(0.14686, 0.10129)
loop_1 = loop_1.lineTo(0.15518, -0.07485)
loop_1 = loop_1.lineTo(0.13702, -0.07155)
loop_1 = loop_1.lineTo(0.11149, -0.06476)
loop_1 = loop_1.lineTo(0.06855, -0.06073)
loop_1 = loop_1.lineTo(0.05792, -0.06026)
loop_1 = loop_1.lineTo(0.02474, -0.05708)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_34_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_34_interval_1.stl')