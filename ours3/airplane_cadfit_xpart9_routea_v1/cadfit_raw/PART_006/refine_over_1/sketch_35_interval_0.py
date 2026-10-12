import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81976, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.75565, 0.10335)
loop_1 = loop_1.lineTo(-0.75522, 0.01492)
loop_1 = loop_1.lineTo(-0.50078, 0.01532)
loop_1 = loop_1.lineTo(-0.54669, 0.02047)
loop_1 = loop_1.threePointArc((-0.57373, 0.02378), (-0.60157, 0.02799))
loop_1 = loop_1.threePointArc((-0.62446, 0.03121), (-0.64803, 0.03488))
loop_1 = loop_1.lineTo(-0.68245, 0.04067)
loop_1 = loop_1.lineTo(-0.70207, 0.0461)
loop_1 = loop_1.threePointArc((-0.7113, 0.05157), (-0.72053, 0.05749))
loop_1 = loop_1.lineTo(-0.73313, 0.06768)
loop_1 = loop_1.lineTo(-0.74939, 0.08799)
loop_1 = loop_1.lineTo(-0.75556, 0.10316)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_35_interval_0.stl')