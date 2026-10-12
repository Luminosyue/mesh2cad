import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73755, 0.58058, 0.03503), normal=(0.95468, -0.29759, 0.00451), xDir=(-0.29759, -0.95469, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.52151, 0.20627)
loop_1 = loop_1.lineTo(0.57108, -0.20695)
loop_1 = loop_1.lineTo(0.52345, -0.21366)
loop_1 = loop_1.lineTo(0.52154, 0.20119)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_4_interval_0.stl')