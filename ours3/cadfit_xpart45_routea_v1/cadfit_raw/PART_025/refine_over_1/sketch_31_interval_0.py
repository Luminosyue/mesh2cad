import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.66597, -0.15665, -0.08417), normal=(0.24856, 0.96862, 0.00047), xDir=(0.96862, -0.24856, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15078, -0.6981)
loop_1 = loop_1.lineTo(0.089, -0.65739)
loop_1 = loop_1.threePointArc((0.0646, -0.64257), (0.0431, -0.62922))
loop_1 = loop_1.threePointArc((0.0098, -0.6065), (-0.02032, -0.58743))
loop_1 = loop_1.threePointArc((-0.04428, -0.57301), (-0.06496, -0.55909))
loop_1 = loop_1.threePointArc((-0.09793, -0.54021), (-0.12885, -0.52077))
loop_1 = loop_1.lineTo(-0.10704, -0.53063)
loop_1 = loop_1.lineTo(0.28017, -0.66972)
loop_1 = loop_1.lineTo(0.31041, -0.66931)
loop_1 = loop_1.threePointArc((0.32723, -0.66887), (0.34013, -0.66854))
loop_1 = loop_1.lineTo(0.30833, -0.68289)
loop_1 = loop_1.threePointArc((0.27274, -0.69025), (0.23932, -0.6969))
loop_1 = loop_1.threePointArc((0.19956, -0.70048), (0.16412, -0.70369))
loop_1 = loop_1.lineTo(0.15078, -0.6981)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_31_interval_0.stl')