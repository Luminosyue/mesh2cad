import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2609, 0.1573, -0.08344), normal=(0.04007, -0.7737, -0.63229), xDir=(-0.99866, -0.05172, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01125, -0.14197)
loop_1 = loop_1.lineTo(-0.10645, -0.14317)
loop_1 = loop_1.lineTo(-0.10692, -0.16958)
loop_1 = loop_1.lineTo(0.01149, -0.16958)
loop_1 = loop_1.lineTo(0.01127, -0.14359)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_13_interval_0.stl')