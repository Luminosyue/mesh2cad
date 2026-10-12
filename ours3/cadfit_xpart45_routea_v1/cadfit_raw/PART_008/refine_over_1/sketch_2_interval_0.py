import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.17856, -0.2285, -0.28443), normal=(0.74781, 0.66357, -0.02138), xDir=(0.66372, -0.74798, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28132, 0.03405)
loop_1 = loop_1.lineTo(0.28232, -0.0203)
loop_1 = loop_1.lineTo(0.25809, -0.0133)
loop_1 = loop_1.lineTo(0.2326, -0.0118)
loop_1 = loop_1.lineTo(0.17902, -0.00185)
loop_1 = loop_1.lineTo(0.162, -0.0018)
loop_1 = loop_1.lineTo(0.09976, 0.00196)
loop_1 = loop_1.lineTo(0.01462, 0.00333)
loop_1 = loop_1.threePointArc((-0.05678, 0.00311), (-0.11973, 0.00175))
loop_1 = loop_1.threePointArc((-0.15734, -0.00034), (-0.19007, -0.00199))
loop_1 = loop_1.threePointArc((-0.22736, -0.01042), (-0.25955, -0.01565))
loop_1 = loop_1.lineTo(-0.26055, 0.02039)
loop_1 = loop_1.lineTo(0.27577, 0.03391)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_2_interval_0.stl')