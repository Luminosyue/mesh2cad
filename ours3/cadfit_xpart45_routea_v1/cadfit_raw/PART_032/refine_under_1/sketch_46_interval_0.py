import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.61, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30654, 0.34714)
loop_1 = loop_1.threePointArc((0.25318, 0.34602), (0.19759, 0.34592))
loop_1 = loop_1.threePointArc((0.15565, 0.3455), (0.11598, 0.34467))
loop_1 = loop_1.threePointArc((0.04299, 0.34569), (-0.0265, 0.3454))
loop_1 = loop_1.threePointArc((-0.09514, 0.34587), (-0.16044, 0.34512))
loop_1 = loop_1.threePointArc((-0.29307, 0.34577), (-0.41979, 0.34422))
loop_1 = loop_1.lineTo(-0.44021, 0.34302)
loop_1 = loop_1.lineTo(0.40769, 0.3437)
loop_1 = loop_1.lineTo(0.35221, 0.34629)
loop_1 = loop_1.threePointArc((0.32893, 0.3468), (0.30716, 0.34709))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.49)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_46_interval_0.stl')