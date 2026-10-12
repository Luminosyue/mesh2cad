import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.20039, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07096, 0.19378)
loop_1 = loop_1.threePointArc((-0.05264, 0.18879), (-0.03494, 0.18444))
loop_1 = loop_1.threePointArc((0.02198, 0.17231), (0.07688, 0.16373))
loop_1 = loop_1.threePointArc((0.10699, 0.16047), (0.13788, 0.156))
loop_1 = loop_1.threePointArc((0.17353, 0.1509), (0.20757, 0.14703))
loop_1 = loop_1.lineTo(0.27281, 0.14007)
loop_1 = loop_1.threePointArc((0.30532, 0.13839), (0.33883, 0.13623))
loop_1 = loop_1.threePointArc((0.37143, 0.1365), (0.40239, 0.13732))
loop_1 = loop_1.lineTo(-0.07063, 0.19378)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_45_interval_0.stl')