import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.6127, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20041, -0.46069)
loop_1 = loop_1.lineTo(-0.1745, -0.4992)
loop_1 = loop_1.lineTo(-0.15466, -0.52397)
loop_1 = loop_1.lineTo(-0.67802, -0.52899)
loop_1 = loop_1.lineTo(-0.27968, -0.36156)
loop_1 = loop_1.lineTo(-0.23431, -0.41127)
loop_1 = loop_1.threePointArc((-0.22863, -0.41723), (-0.22421, -0.4241))
loop_1 = loop_1.lineTo(-0.20062, -0.46036)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_76_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_76_interval_0.stl')