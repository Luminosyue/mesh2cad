import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.15188), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87959, 0.53269)
loop_1 = loop_1.lineTo(-0.87939, 0.44415)
loop_1 = loop_1.lineTo(-0.862, 0.47074)
loop_1 = loop_1.lineTo(-0.83389, 0.50542)
loop_1 = loop_1.lineTo(-0.82322, 0.51808)
loop_1 = loop_1.lineTo(-0.81196, 0.53269)
loop_1 = loop_1.lineTo(-0.8795, 0.53269)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_60_interval_0.stl')