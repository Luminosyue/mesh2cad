import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.79959), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02511, 0.40114)
loop_1 = loop_1.threePointArc((-0.00944, 0.40009), (0.00686, 0.39872))
loop_1 = loop_1.threePointArc((0.02291, 0.39693), (0.03948, 0.39489))
loop_1 = loop_1.threePointArc((0.05669, 0.39115), (0.07317, 0.38794))
loop_1 = loop_1.threePointArc((0.08972, 0.38291), (0.10675, 0.37741))
loop_1 = loop_1.threePointArc((0.12218, 0.3713), (0.13025, 0.36812))
loop_1 = loop_1.lineTo(0.13005, 0.40114)
loop_1 = loop_1.lineTo(-0.025, 0.40114)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.78)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_39_interval_0.stl')