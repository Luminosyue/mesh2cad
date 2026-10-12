import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.48309, -0.30831, 0.14922), normal=(-0.86334, 0.50462, 3e-05), xDir=(0.50462, 0.86334, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34708, -0.16227)
loop_1 = loop_1.lineTo(-0.3471, -0.38009)
loop_1 = loop_1.lineTo(-0.31182, -0.38009)
loop_1 = loop_1.lineTo(-0.3191, -0.36668)
loop_1 = loop_1.lineTo(-0.33341, -0.32682)
loop_1 = loop_1.lineTo(-0.33514, -0.30013)
loop_1 = loop_1.lineTo(-0.33606, -0.27481)
loop_1 = loop_1.threePointArc((-0.33841, -0.25671), (-0.34049, -0.24163))
loop_1 = loop_1.lineTo(-0.34335, -0.2228)
loop_1 = loop_1.lineTo(-0.34562, -0.1893)
loop_1 = loop_1.threePointArc((-0.34597, -0.17875), (-0.34624, -0.1708))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_23_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_23_interval_1.stl')