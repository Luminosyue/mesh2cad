import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.59084), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41055, -0.80792)
loop_1 = loop_1.lineTo(0.41935, -0.91554)
loop_1 = loop_1.lineTo(0.00809, -0.91501)
loop_1 = loop_1.lineTo(0.0432, -0.91295)
loop_1 = loop_1.threePointArc((0.09399, -0.90758), (0.14225, -0.90078))
loop_1 = loop_1.lineTo(0.19914, -0.89024)
loop_1 = loop_1.lineTo(0.24904, -0.8767)
loop_1 = loop_1.lineTo(0.30164, -0.85878)
loop_1 = loop_1.lineTo(0.39633, -0.81413)
loop_1 = loop_1.threePointArc((0.40317, -0.81079), (0.41028, -0.80812))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_92_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_92_interval_0.stl')