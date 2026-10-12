import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81949, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70369, 0.22714)
loop_1 = loop_1.lineTo(-0.38216, 0.1384)
loop_1 = loop_1.threePointArc((-0.39996, 0.14085), (-0.41817, 0.14384))
loop_1 = loop_1.threePointArc((-0.45949, 0.15109), (-0.50182, 0.16084))
loop_1 = loop_1.lineTo(-0.52908, 0.16712)
loop_1 = loop_1.threePointArc((-0.55508, 0.17344), (-0.57992, 0.17895))
loop_1 = loop_1.threePointArc((-0.59183, 0.18196), (-0.60318, 0.18406))
loop_1 = loop_1.threePointArc((-0.61269, 0.18626), (-0.62229, 0.18872))
loop_1 = loop_1.threePointArc((-0.6337, 0.19096), (-0.64447, 0.19278))
loop_1 = loop_1.threePointArc((-0.65288, 0.19376), (-0.66132, 0.19519))
loop_1 = loop_1.lineTo(-0.68217, 0.19202)
loop_1 = loop_1.threePointArc((-0.6926, 0.1882), (-0.70219, 0.18414))
loop_1 = loop_1.lineTo(-0.71869, 0.17178)
loop_1 = loop_1.lineTo(-0.70375, 0.2269)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_30_interval_0.stl')