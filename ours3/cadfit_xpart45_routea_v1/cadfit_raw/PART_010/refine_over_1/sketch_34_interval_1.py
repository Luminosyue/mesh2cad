import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59196, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.25124, -0.64761)
loop_1 = loop_1.lineTo(-0.22791, -0.64936)
loop_1 = loop_1.lineTo(-0.25291, -0.67111)
loop_1 = loop_1.lineTo(-0.28919, -0.6725)
loop_1 = loop_1.lineTo(-0.32117, -0.64805)
loop_1 = loop_1.threePointArc((-0.28695, -0.64774), (-0.25131, -0.64764))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.94)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_34_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_34_interval_1.stl')