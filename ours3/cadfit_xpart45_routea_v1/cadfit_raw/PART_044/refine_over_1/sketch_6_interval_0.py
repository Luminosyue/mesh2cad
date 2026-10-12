import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2139, -0.0137, -0.0359), normal=(0.57202, 0.82024, 0.00013), xDir=(0.82024, -0.57202, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11816, 0.8041)
loop_1 = loop_1.lineTo(0.11787, 0.48274)
loop_1 = loop_1.lineTo(0.11754, 0.49281)
loop_1 = loop_1.lineTo(0.11503, 0.52575)
loop_1 = loop_1.lineTo(0.1142, 0.5367)
loop_1 = loop_1.threePointArc((0.11259, 0.5533), (0.11107, 0.56587))
loop_1 = loop_1.lineTo(0.11029, 0.57698)
loop_1 = loop_1.lineTo(0.10994, 0.58701)
loop_1 = loop_1.lineTo(0.10695, 0.62684)
loop_1 = loop_1.threePointArc((0.10569, 0.66015), (0.10568, 0.69152))
loop_1 = loop_1.threePointArc((0.10595, 0.70519), (0.10618, 0.71509))
loop_1 = loop_1.lineTo(0.10582, 0.73182)
loop_1 = loop_1.lineTo(0.10654, 0.75144)
loop_1 = loop_1.threePointArc((0.1071, 0.78029), (0.10719, 0.8041))
loop_1 = loop_1.lineTo(0.11816, 0.8041)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_6_interval_0.stl')