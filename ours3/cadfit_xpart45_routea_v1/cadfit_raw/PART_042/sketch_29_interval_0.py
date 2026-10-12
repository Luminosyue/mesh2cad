import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98398, 0.03143, -0.05766), normal=(0.99863, 0.05217, 0.00296), xDir=(0.05217, -0.99864, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05516, -0.31387)
loop_1 = loop_1.lineTo(-0.06857, -0.32508)
loop_1 = loop_1.lineTo(-0.07172, -0.34403)
loop_1 = loop_1.lineTo(-0.06816, -0.3541)
loop_1 = loop_1.lineTo(-0.06396, -0.36465)
loop_1 = loop_1.lineTo(-0.04858, -0.37199)
loop_1 = loop_1.lineTo(-0.02957, -0.36694)
loop_1 = loop_1.lineTo(-0.02512, -0.34761)
loop_1 = loop_1.lineTo(-0.03229, -0.32382)
loop_1 = loop_1.lineTo(-0.05432, -0.31397)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.99)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_29_interval_0.stl')