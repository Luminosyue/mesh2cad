import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.91456, -0.1496, 0.04032), normal=(0.99049, -0.13755, 0.00386), xDir=(-0.13755, -0.99049, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30422, -0.08535)
loop_1 = loop_1.lineTo(-0.30404, -0.4202)
loop_1 = loop_1.lineTo(-0.28294, -0.36334)
loop_1 = loop_1.lineTo(-0.26135, -0.23779)
loop_1 = loop_1.lineTo(-0.26467, -0.11325)
loop_1 = loop_1.lineTo(-0.30133, -0.08739)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_34_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_34_interval_1.stl')