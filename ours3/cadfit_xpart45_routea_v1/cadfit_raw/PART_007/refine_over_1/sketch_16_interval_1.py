import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.52523, 0.47619, 0.47822), normal=(0.72794, -0.007, 0.6856), xDir=(-0.00961, -0.99995, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.43606, -0.13174)
loop_1 = loop_1.lineTo(-0.50424, -0.13174)
loop_1 = loop_1.threePointArc((-0.48479, -0.15531), (-0.47334, -0.16957))
loop_1 = loop_1.lineTo(-0.45699, -0.17027)
loop_1 = loop_1.threePointArc((-0.40653, -0.17075), (-0.35814, -0.1682))
loop_1 = loop_1.threePointArc((0.38009, -0.16509), (1.08532, -0.15873))
loop_1 = loop_1.lineTo(1.10458, -0.15752)
loop_1 = loop_1.threePointArc((1.25574, -0.15388), (1.41325, -0.15243))
loop_1 = loop_1.lineTo(1.43606, -0.13174)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_16_interval_1.stl')