import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0279, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87785, 0.13047)
loop_1 = loop_1.lineTo(-0.8025, 0.12934)
loop_1 = loop_1.lineTo(-0.83165, 0.12068)
loop_1 = loop_1.lineTo(-0.85211, 0.1111)
loop_1 = loop_1.lineTo(-0.87317, 0.09875)
loop_1 = loop_1.lineTo(-0.87786, 0.13041)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_30_interval_0.stl')