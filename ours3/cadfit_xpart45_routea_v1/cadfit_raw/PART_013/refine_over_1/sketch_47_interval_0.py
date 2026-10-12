import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29821, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.68259, 0.14945)
loop_1 = loop_1.lineTo(-0.68278, 0.0954)
loop_1 = loop_1.lineTo(-0.79056, 0.09563)
loop_1 = loop_1.lineTo(-0.77322, 0.10196)
loop_1 = loop_1.lineTo(-0.75147, 0.12127)
loop_1 = loop_1.threePointArc((-0.7399, 0.13077), (-0.73461, 0.13429))
loop_1 = loop_1.lineTo(-0.68269, 0.14943)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_47_interval_0.stl')