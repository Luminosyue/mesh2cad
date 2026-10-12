import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.16718, 0.03528, 0.24834), normal=(0.00053, 0.00185, -1.0), xDir=(0.0, -1.0, -0.00185))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70621, 0.381)
loop_1 = loop_1.lineTo(-0.71918, 0.36296)
loop_1 = loop_1.lineTo(-0.73231, 0.34475)
loop_1 = loop_1.lineTo(-0.74854, 0.32301)
loop_1 = loop_1.lineTo(-0.76063, 0.30292)
loop_1 = loop_1.lineTo(-0.7606, 0.381)
loop_1 = loop_1.lineTo(-0.70734, 0.381)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_8_interval_0.stl')