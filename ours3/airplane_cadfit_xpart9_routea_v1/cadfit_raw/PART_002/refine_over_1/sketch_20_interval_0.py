import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5786, 0.23184, 0.0799), normal=(-0.05975, -0.92489, 0.37552), xDir=(-0.99792, 0.06447, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.19043, 0.51549)
loop_1 = loop_1.lineTo(-1.2031, 0.51525)
loop_1 = loop_1.lineTo(-1.21614, 0.51437)
loop_1 = loop_1.lineTo(-1.24707, 0.50961)
loop_1 = loop_1.lineTo(-1.26361, 0.50208)
loop_1 = loop_1.lineTo(-1.06854, 0.49222)
loop_1 = loop_1.lineTo(-1.10357, 0.50581)
loop_1 = loop_1.lineTo(-1.14448, 0.51365)
loop_1 = loop_1.lineTo(-1.17738, 0.51514)
loop_1 = loop_1.lineTo(-1.19028, 0.51549)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_20_interval_0.stl')