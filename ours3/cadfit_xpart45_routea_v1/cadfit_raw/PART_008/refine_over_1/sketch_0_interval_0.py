import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.12552, -0.01892, -0.27617), normal=(0.99375, 0.10743, -0.03047), xDir=(0.10748, -0.99421, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.29841, 0.04061)
loop_1 = loop_1.lineTo(0.29899, -0.02145)
loop_1 = loop_1.threePointArc((0.26722, -0.01493), (0.24022, -0.00949))
loop_1 = loop_1.lineTo(0.1864, -0.00084)
loop_1 = loop_1.threePointArc((0.12957, 0.00109), (0.08125, 0.00191))
loop_1 = loop_1.threePointArc((0.02404, 0.00221), (-0.0247, 0.00114))
loop_1 = loop_1.lineTo(-0.05038, 0.00178)
loop_1 = loop_1.lineTo(-0.07768, 0.00108)
loop_1 = loop_1.lineTo(-0.10977, 0.00154)
loop_1 = loop_1.lineTo(-0.13065, 6e-05)
loop_1 = loop_1.lineTo(-0.16911, 6e-05)
loop_1 = loop_1.lineTo(-0.18362, -0.00254)
loop_1 = loop_1.lineTo(-0.22865, -0.00492)
loop_1 = loop_1.lineTo(-0.24342, -0.00868)
loop_1 = loop_1.lineTo(-0.27946, -0.01653)
loop_1 = loop_1.lineTo(-0.27994, 0.03527)
loop_1 = loop_1.lineTo(0.29632, 0.04059)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_0_interval_0.stl')