import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.73908, 0.35496, -0.00475), normal=(0.82718, 0.56192, -0.0046), xDir=(0.56193, -0.82718, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.68905, 0.15044)
loop_1 = loop_1.lineTo(-0.67167, 0.14508)
loop_1 = loop_1.lineTo(-0.66293, 0.13072)
loop_1 = loop_1.lineTo(-0.64972, 0.11299)
loop_1 = loop_1.lineTo(-0.64035, 0.08055)
loop_1 = loop_1.lineTo(-0.64096, 0.06995)
loop_1 = loop_1.lineTo(-0.64468, 0.03038)
loop_1 = loop_1.lineTo(-0.66979, -0.00426)
loop_1 = loop_1.lineTo(-0.67988, -0.0198)
loop_1 = loop_1.lineTo(-0.70534, -0.0198)
loop_1 = loop_1.lineTo(-0.71722, -0.01288)
loop_1 = loop_1.lineTo(-0.73781, 0.02069)
loop_1 = loop_1.lineTo(-0.74943, 0.06385)
loop_1 = loop_1.lineTo(-0.74253, 0.10247)
loop_1 = loop_1.lineTo(-0.72448, 0.13072)
loop_1 = loop_1.lineTo(-0.71374, 0.14173)
loop_1 = loop_1.lineTo(-0.69111, 0.14972)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_033/sketch_9_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_033/sketch_9_interval_1.stl')