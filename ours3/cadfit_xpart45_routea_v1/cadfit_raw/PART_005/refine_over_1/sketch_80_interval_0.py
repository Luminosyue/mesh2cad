import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.4827, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.97562, -0.428)
loop_1 = loop_1.lineTo(0.96421, -0.09085)
loop_1 = loop_1.lineTo(0.9738, -0.10788)
loop_1 = loop_1.threePointArc((0.97597, -0.13415), (0.97787, -0.16131))
loop_1 = loop_1.threePointArc((0.97781, -0.19379), (0.97819, -0.22476))
loop_1 = loop_1.threePointArc((0.97733, -0.273), (0.97743, -0.31909))
loop_1 = loop_1.lineTo(0.97725, -0.37435)
loop_1 = loop_1.lineTo(0.97563, -0.42708)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.91)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_80_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_80_interval_0.stl')