import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.22029, 0.0153, -0.02362), normal=(0.00066, 0.64956, 0.76031), xDir=(1.0, -0.00102, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13598, 0.04389)
loop_1 = loop_1.lineTo(-0.64839, 0.04041)
loop_1 = loop_1.lineTo(-0.75752, 0.03609)
loop_1 = loop_1.lineTo(-0.76931, 0.02839)
loop_1 = loop_1.threePointArc((-0.77351, 0.01974), (-0.77844, 0.01103))
loop_1 = loop_1.threePointArc((-0.77954, -0.01333), (-0.77685, -0.03462))
loop_1 = loop_1.lineTo(-0.76776, -0.05543)
loop_1 = loop_1.lineTo(-0.75062, -0.06803)
loop_1 = loop_1.threePointArc((0.01284, -0.06812), (0.7431, -0.06678))
loop_1 = loop_1.lineTo(1.06109, -0.06754)
loop_1 = loop_1.lineTo(1.06751, -0.05051)
loop_1 = loop_1.threePointArc((1.05875, -0.03126), (1.0472, -0.01455))
loop_1 = loop_1.lineTo(0.94505, 0.03483)
loop_1 = loop_1.threePointArc((0.9133, 0.04103), (0.88626, 0.04179))
loop_1 = loop_1.threePointArc((0.70543, 0.04338), (0.53618, 0.04134))
loop_1 = loop_1.lineTo(0.19054, 0.04075)
loop_1 = loop_1.threePointArc((0.16086, 0.04332), (0.13641, 0.04382))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_16_interval_0.stl')