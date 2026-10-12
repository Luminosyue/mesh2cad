import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03346, -0.06243)
loop_1 = loop_1.lineTo(-0.00755, -0.06468)
loop_1 = loop_1.lineTo(-0.02552, -0.06817)
loop_1 = loop_1.lineTo(-0.04521, -0.07426)
loop_1 = loop_1.lineTo(-0.06218, -0.08422)
loop_1 = loop_1.lineTo(-0.06683, -0.10371)
loop_1 = loop_1.lineTo(-0.04637, -0.12338)
loop_1 = loop_1.threePointArc((0.07713, -0.14593), (0.18939, -0.10229))
loop_1 = loop_1.lineTo(0.16905, -0.09108)
loop_1 = loop_1.lineTo(0.15163, -0.08293)
loop_1 = loop_1.lineTo(0.13018, -0.07541)
loop_1 = loop_1.lineTo(0.11065, -0.06966)
loop_1 = loop_1.lineTo(0.0911, -0.06581)
loop_1 = loop_1.threePointArc((0.08068, -0.06465), (0.07087, -0.06376))
loop_1 = loop_1.threePointArc((0.05253, -0.06325), (0.03366, -0.06242))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/greedy_greedy_step_extrude.stl')