import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.51196, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.1069, -0.78769)
loop_1 = loop_1.threePointArc((0.11521, -0.7882), (0.12383, -0.78911))
loop_1 = loop_1.lineTo(0.14983, -0.79179)
loop_1 = loop_1.lineTo(0.17503, -0.80994)
loop_1 = loop_1.lineTo(0.18696, -0.82785)
loop_1 = loop_1.lineTo(0.19719, -0.84661)
loop_1 = loop_1.lineTo(0.22268, -0.87802)
loop_1 = loop_1.lineTo(0.25917, -0.90431)
loop_1 = loop_1.lineTo(0.27344, -0.90857)
loop_1 = loop_1.lineTo(0.10665, -0.90778)
loop_1 = loop_1.lineTo(0.1069, -0.78786)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.62)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_32_interval_0.stl')