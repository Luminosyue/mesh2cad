import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.14523), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35263, 0.4808)
loop_1 = loop_1.lineTo(0.32354, 0.13151)
loop_1 = loop_1.threePointArc((0.32437, 0.15261), (0.32478, 0.17264))
loop_1 = loop_1.threePointArc((0.32465, 0.18689), (0.32536, 0.20145))
loop_1 = loop_1.threePointArc((0.32584, 0.22042), (0.32592, 0.2384))
loop_1 = loop_1.threePointArc((0.32669, 0.25309), (0.3268, 0.26697))
loop_1 = loop_1.lineTo(0.32642, 0.31869)
loop_1 = loop_1.lineTo(0.32653, 0.34283)
loop_1 = loop_1.lineTo(0.32676, 0.37016)
loop_1 = loop_1.lineTo(0.32811, 0.41597)
loop_1 = loop_1.lineTo(0.32879, 0.43578)
loop_1 = loop_1.threePointArc((0.33037, 0.44749), (0.33152, 0.45855))
loop_1 = loop_1.lineTo(0.33722, 0.47911)
loop_1 = loop_1.lineTo(0.35241, 0.48085)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_54_interval_0.stl')