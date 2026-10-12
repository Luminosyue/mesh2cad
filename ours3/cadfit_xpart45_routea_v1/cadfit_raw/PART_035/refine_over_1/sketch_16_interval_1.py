import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.3091, -0.48495, 0.01019), normal=(0.42789, -0.90382, -0.00353), xDir=(-0.90383, -0.42789, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.41034, 0.15515)
loop_1 = loop_1.lineTo(-0.41131, 0.1419)
loop_1 = loop_1.lineTo(-0.41455, 0.11968)
loop_1 = loop_1.lineTo(-0.41361, 0.1081)
loop_1 = loop_1.lineTo(-0.41489, 0.08439)
loop_1 = loop_1.lineTo(-0.41438, 0.26394)
loop_1 = loop_1.lineTo(-0.36908, 0.26394)
loop_1 = loop_1.lineTo(-0.40882, 0.16682)
loop_1 = loop_1.lineTo(-0.41034, 0.15515)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_16_interval_1.stl')