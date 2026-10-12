import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.58915, -0.77244, 0.04244), normal=(0.47697, 0.87884, -0.01175), xDir=(0.8789, -0.477, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39775, 0.17743)
loop_1 = loop_1.lineTo(-0.39886, -0.2126)
loop_1 = loop_1.lineTo(0.34526, -0.2126)
loop_1 = loop_1.lineTo(0.35381, 0.17743)
loop_1 = loop_1.lineTo(-0.38795, 0.17743)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_7_interval_0.stl')