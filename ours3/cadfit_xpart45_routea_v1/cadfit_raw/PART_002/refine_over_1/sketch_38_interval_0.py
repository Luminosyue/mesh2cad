import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03244, 0.01038, 0.11821), normal=(0.00036, -0.99292, -0.11878), xDir=(-1.0, -0.00036, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00391, 1.08133)
loop_1 = loop_1.lineTo(0.04104, 1.08068)
loop_1 = loop_1.lineTo(0.07474, 1.07874)
loop_1 = loop_1.lineTo(0.10835, 1.07548)
loop_1 = loop_1.lineTo(0.13848, 1.07146)
loop_1 = loop_1.lineTo(0.15232, 1.0702)
loop_1 = loop_1.lineTo(-0.19295, 1.06945)
loop_1 = loop_1.lineTo(-0.17117, 1.07131)
loop_1 = loop_1.lineTo(-0.12806, 1.07298)
loop_1 = loop_1.lineTo(0.0039, 1.08133)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_38_interval_0.stl')