import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.555, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.7, 0.76809)
loop_1 = loop_1.lineTo(-0.50227, 0.76759)
loop_1 = loop_1.threePointArc((-0.51677, 0.75813), (-0.53218, 0.74915))
loop_1 = loop_1.threePointArc((-0.56537, 0.72963), (-0.59692, 0.71074))
loop_1 = loop_1.threePointArc((-0.61126, 0.70192), (-0.62615, 0.69302))
loop_1 = loop_1.threePointArc((-0.6629, 0.67142), (-0.69783, 0.65044))
loop_1 = loop_1.lineTo(-0.7, 0.76791)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_37_interval_0.stl')