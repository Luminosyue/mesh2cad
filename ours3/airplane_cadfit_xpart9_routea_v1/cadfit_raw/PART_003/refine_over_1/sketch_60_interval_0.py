import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.28075), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12901, -0.4208)
loop_1 = loop_1.lineTo(-0.02015, -0.41999)
loop_1 = loop_1.lineTo(-0.02098, 0.1225)
loop_1 = loop_1.lineTo(-0.02904, 0.06177)
loop_1 = loop_1.lineTo(-0.03768, -0.01005)
loop_1 = loop_1.lineTo(-0.04141, -0.04693)
loop_1 = loop_1.threePointArc((-0.04472, -0.07724), (-0.04731, -0.10599))
loop_1 = loop_1.lineTo(-0.05665, -0.16695)
loop_1 = loop_1.threePointArc((-0.06165, -0.19708), (-0.06763, -0.22789))
loop_1 = loop_1.lineTo(-0.07301, -0.25866)
loop_1 = loop_1.lineTo(-0.08384, -0.3079)
loop_1 = loop_1.lineTo(-0.09531, -0.34995)
loop_1 = loop_1.threePointArc((-0.10242, -0.36812), (-0.10811, -0.38555))
loop_1 = loop_1.lineTo(-0.11813, -0.40951)
loop_1 = loop_1.threePointArc((-0.12338, -0.41513), (-0.12869, -0.42053))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_60_interval_0.stl')