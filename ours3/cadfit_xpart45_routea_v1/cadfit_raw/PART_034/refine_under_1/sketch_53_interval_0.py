import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.79, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15101, 0.23159)
loop_1 = loop_1.threePointArc((-0.21056, 0.23058), (-0.27259, 0.23109))
loop_1 = loop_1.threePointArc((-0.35282, 0.22971), (-0.43528, 0.2303))
loop_1 = loop_1.threePointArc((-0.5929, 0.22889), (-0.7431, 0.22378))
loop_1 = loop_1.lineTo(-0.78936, 0.20862)
loop_1 = loop_1.lineTo(0.77197, 0.20874)
loop_1 = loop_1.lineTo(0.72769, 0.22508)
loop_1 = loop_1.threePointArc((0.63937, 0.22879), (0.55552, 0.22921))
loop_1 = loop_1.threePointArc((0.43763, 0.23025), (0.32547, 0.22955))
loop_1 = loop_1.threePointArc((0.14257, 0.23104), (-0.032, 0.23011))
loop_1 = loop_1.lineTo(-0.14996, 0.23143)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_53_interval_0.stl')