import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47358, 0.76462, -0.06766), normal=(0.51795, 0.85541, 5e-05), xDir=(0.85541, -0.51795, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31585, -0.52728)
loop_1 = loop_1.lineTo(0.31356, -0.54375)
loop_1 = loop_1.lineTo(0.29696, -0.56834)
loop_1 = loop_1.lineTo(0.28265, -0.59029)
loop_1 = loop_1.lineTo(0.31586, -0.59702)
loop_1 = loop_1.lineTo(0.31585, -0.52828)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_6_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_6_interval_2.stl')