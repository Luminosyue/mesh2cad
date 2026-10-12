import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.99171, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.57366, 0.38149)
loop_1 = loop_1.lineTo(-0.56134, 0.40287)
loop_1 = loop_1.lineTo(-0.56142, 0.42)
loop_1 = loop_1.lineTo(-0.60677, 0.41984)
loop_1 = loop_1.lineTo(-0.5893, 0.34592)
loop_1 = loop_1.lineTo(-0.59662, 0.32899)
loop_1 = loop_1.lineTo(-0.58862, 0.34641)
loop_1 = loop_1.lineTo(-0.5737, 0.38142)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.99)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_51_interval_0.stl')