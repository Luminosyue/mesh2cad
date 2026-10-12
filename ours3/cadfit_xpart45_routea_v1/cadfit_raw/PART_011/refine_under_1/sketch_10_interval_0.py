import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.3452, -0.84867, -0.0447), normal=(-0.57745, 0.81606, 0.02444), xDir=(0.8163, 0.57763, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27561, 0.17561)
loop_1 = loop_1.lineTo(-0.26131, -0.21039)
loop_1 = loop_1.lineTo(-0.26496, -0.19004)
loop_1 = loop_1.lineTo(-0.26586, -0.14078)
loop_1 = loop_1.lineTo(-0.26979, -0.08872)
loop_1 = loop_1.threePointArc((-0.27178, -0.03857), (-0.27398, 0.00576))
loop_1 = loop_1.lineTo(-0.27625, 0.05479)
loop_1 = loop_1.threePointArc((-0.27669, 0.1038), (-0.27724, 0.14679))
loop_1 = loop_1.threePointArc((-0.27655, 0.16092), (-0.27584, 0.17194))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_10_interval_0.stl')