import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.63195, 0.69356, 0.01796), normal=(0.5598, -0.82863, 0.00049), xDir=(-0.82863, -0.5598, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.19598, -0.17978)
loop_1 = loop_1.lineTo(-0.21437, -0.1872)
loop_1 = loop_1.lineTo(-0.21439, -0.23286)
loop_1 = loop_1.lineTo(-0.19039, -0.22991)
loop_1 = loop_1.threePointArc((-0.168, -0.21704), (-0.14678, -0.20474))
loop_1 = loop_1.lineTo(-0.11762, -0.18767)
loop_1 = loop_1.lineTo(-0.13233, -0.18831)
loop_1 = loop_1.lineTo(-0.16628, -0.18095)
loop_1 = loop_1.lineTo(-0.19176, -0.17631)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_16_interval_0.stl')