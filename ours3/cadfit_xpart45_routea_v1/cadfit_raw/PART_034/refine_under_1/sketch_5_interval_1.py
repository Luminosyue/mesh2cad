import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.43214, 0.68757, 0.01766), normal=(0.48756, 0.87304, -0.00905), xDir=(0.87308, -0.48758, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.3936, 0.15506)
loop_1 = loop_1.lineTo(-0.39884, -0.09853)
loop_1 = loop_1.lineTo(-0.3998, -0.07589)
loop_1 = loop_1.threePointArc((-0.3997, -0.05504), (-0.39908, -0.03596))
loop_1 = loop_1.threePointArc((-0.39859, -0.02041), (-0.39802, -0.00681))
loop_1 = loop_1.lineTo(-0.39969, 0.02565)
loop_1 = loop_1.lineTo(-0.40005, 0.04216)
loop_1 = loop_1.lineTo(-0.40268, 0.07076)
loop_1 = loop_1.lineTo(-0.40352, 0.09112)
loop_1 = loop_1.threePointArc((-0.40218, 0.11647), (-0.40056, 0.14008))
loop_1 = loop_1.lineTo(-0.39479, 0.15251)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_5_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_5_interval_1.stl')