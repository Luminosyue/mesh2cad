import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.555, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34, -0.75622)
loop_1 = loop_1.lineTo(0.33988, -0.79354)
loop_1 = loop_1.lineTo(0.27692, -0.79339)
loop_1 = loop_1.threePointArc((0.29217, -0.7844), (0.30809, -0.7752))
loop_1 = loop_1.threePointArc((0.31869, -0.769), (0.32881, -0.76305))
loop_1 = loop_1.lineTo(0.33995, -0.75625)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_39_interval_0.stl')