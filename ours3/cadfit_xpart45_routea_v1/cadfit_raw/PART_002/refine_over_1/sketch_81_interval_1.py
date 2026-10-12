import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.19373, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39225, -0.50117)
loop_1 = loop_1.lineTo(-0.39157, -0.81)
loop_1 = loop_1.lineTo(-0.13184, -0.80943)
loop_1 = loop_1.lineTo(-0.15973, -0.8031)
loop_1 = loop_1.threePointArc((-0.17723, -0.79643), (-0.19382, -0.79041))
loop_1 = loop_1.lineTo(-0.23464, -0.7658)
loop_1 = loop_1.threePointArc((-0.25362, -0.75158), (-0.27284, -0.73667))
loop_1 = loop_1.lineTo(-0.28404, -0.72764)
loop_1 = loop_1.lineTo(-0.30539, -0.71346)
loop_1 = loop_1.lineTo(-0.34126, -0.68942)
loop_1 = loop_1.lineTo(-0.37906, -0.65442)
loop_1 = loop_1.lineTo(-0.385, -0.61601)
loop_1 = loop_1.lineTo(-0.38733, -0.57111)
loop_1 = loop_1.lineTo(-0.38896, -0.53988)
loop_1 = loop_1.lineTo(-0.39127, -0.50528)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_81_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_81_interval_1.stl')