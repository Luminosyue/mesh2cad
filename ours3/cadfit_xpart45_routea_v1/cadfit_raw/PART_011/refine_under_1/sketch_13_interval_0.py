import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00238, 0.89505, -0.00456), normal=(-0.00028, -0.99948, -0.03231), xDir=(-1.0, 0.00028, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34566, -0.18109)
loop_1 = loop_1.lineTo(0.34706, 0.24387)
loop_1 = loop_1.lineTo(-0.34637, 0.23743)
loop_1 = loop_1.lineTo(-0.33153, -0.18109)
loop_1 = loop_1.lineTo(0.33456, -0.18109)
loop_1 = loop_1.lineTo(0.34566, -0.18109)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_13_interval_0.stl')