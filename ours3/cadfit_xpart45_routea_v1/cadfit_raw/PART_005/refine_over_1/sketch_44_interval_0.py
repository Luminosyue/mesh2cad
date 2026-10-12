import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0075, 0.43, 0.07756), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.88932, 0.17461)
loop_1 = loop_1.lineTo(-0.8658, 0.12564)
loop_1 = loop_1.lineTo(-0.82143, 0.07381)
loop_1 = loop_1.lineTo(-0.84096, 0.02197)
loop_1 = loop_1.lineTo(-0.86428, 0.00871)
loop_1 = loop_1.lineTo(-0.89401, -0.02986)
loop_1 = loop_1.lineTo(-0.8988, -0.07364)
loop_1 = loop_1.lineTo(-0.8988, 0.21697)
loop_1 = loop_1.lineTo(-0.89209, 0.18429)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_44_interval_0.stl')