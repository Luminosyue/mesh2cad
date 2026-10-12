import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12534, -0.39605, 0.04967), normal=(0.00148, 1.0, -0.00071), xDir=(1.0, -0.00148, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.45536, -0.80334)
loop_1 = loop_1.lineTo(-0.43154, -0.81072)
loop_1 = loop_1.threePointArc((-0.41406, -0.81538), (-0.40059, -0.81869))
loop_1 = loop_1.lineTo(-0.37337, -0.82647)
loop_1 = loop_1.threePointArc((-0.32925, -0.83799), (-0.287, -0.84981))
loop_1 = loop_1.lineTo(-0.2745, -0.85293)
loop_1 = loop_1.threePointArc((-0.25868, -0.85723), (-0.24339, -0.86093))
loop_1 = loop_1.threePointArc((-0.222, -0.86688), (-0.20471, -0.87123))
loop_1 = loop_1.threePointArc((-0.18163, -0.87764), (-0.16273, -0.88253))
loop_1 = loop_1.lineTo(-0.14394, -0.88777)
loop_1 = loop_1.lineTo(-0.12479, -0.89166)
loop_1 = loop_1.lineTo(-0.45536, -0.89187)
loop_1 = loop_1.lineTo(-0.45536, -0.80361)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/greedy_greedy_step_extrude.stl')