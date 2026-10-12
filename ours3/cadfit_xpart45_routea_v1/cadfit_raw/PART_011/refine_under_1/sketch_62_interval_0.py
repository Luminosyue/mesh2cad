import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.85, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17364, 0.30323)
loop_1 = loop_1.threePointArc((0.24191, 0.30178), (0.31299, 0.29889))
loop_1 = loop_1.threePointArc((0.34178, 0.29774), (0.36891, 0.29763))
loop_1 = loop_1.lineTo(-0.41467, 0.2978)
loop_1 = loop_1.lineTo(-0.2814, 0.29872)
loop_1 = loop_1.threePointArc((-0.25856, 0.29842), (-0.23717, 0.29881))
loop_1 = loop_1.threePointArc((-0.14153, 0.29913), (-0.05028, 0.30181))
loop_1 = loop_1.lineTo(0.12167, 0.30321)
loop_1 = loop_1.threePointArc((0.14817, 0.30314), (0.17309, 0.3034))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_62_interval_0.stl')