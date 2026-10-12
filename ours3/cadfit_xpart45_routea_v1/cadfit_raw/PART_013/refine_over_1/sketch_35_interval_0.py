import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25796, -0.91125, -0.04614), normal=(0.32662, 0.94383, 0.05), xDir=(0.94502, -0.32703, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29682, 0.15325)
loop_1 = loop_1.lineTo(-0.29582, 0.09523)
loop_1 = loop_1.lineTo(-0.29172, 0.10551)
loop_1 = loop_1.lineTo(-0.27779, 0.11225)
loop_1 = loop_1.lineTo(-0.24906, 0.12633)
loop_1 = loop_1.lineTo(-0.23006, 0.13518)
loop_1 = loop_1.lineTo(-0.20355, 0.13515)
loop_1 = loop_1.lineTo(-0.22478, 0.14159)
loop_1 = loop_1.lineTo(-0.23792, 0.14586)
loop_1 = loop_1.lineTo(-0.25515, 0.14938)
loop_1 = loop_1.lineTo(-0.27543, 0.15167)
loop_1 = loop_1.lineTo(-0.2955, 0.15315)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_35_interval_0.stl')