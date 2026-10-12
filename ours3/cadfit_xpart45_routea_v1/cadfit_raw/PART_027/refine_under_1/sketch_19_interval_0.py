import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.12089, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09182, -0.01227)
loop_1 = loop_1.lineTo(0.16715, -0.01215)
loop_1 = loop_1.lineTo(0.18384, -0.01126)
loop_1 = loop_1.lineTo(0.18137, -0.02624)
loop_1 = loop_1.lineTo(0.16942, -0.04525)
loop_1 = loop_1.lineTo(0.15651, -0.05754)
loop_1 = loop_1.lineTo(0.14538, -0.06507)
loop_1 = loop_1.lineTo(0.11751, -0.0745)
loop_1 = loop_1.lineTo(0.09802, -0.07091)
loop_1 = loop_1.lineTo(0.07921, -0.04901)
loop_1 = loop_1.threePointArc((0.07736, -0.03665), (0.07735, -0.0283))
loop_1 = loop_1.lineTo(0.08247, -0.00554)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_19_interval_0.stl')