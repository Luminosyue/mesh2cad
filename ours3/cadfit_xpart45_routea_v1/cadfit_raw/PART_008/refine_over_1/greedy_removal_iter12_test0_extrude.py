import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1368, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.84118, 0.32169)
loop_1 = loop_1.lineTo(0.84112, 0.30835)
loop_1 = loop_1.lineTo(0.82979, 0.31339)
loop_1 = loop_1.threePointArc((0.76795, 0.31466), (0.70943, 0.31337))
loop_1 = loop_1.lineTo(0.3296, 0.3124)
loop_1 = loop_1.lineTo(0.19423, 0.31188)
loop_1 = loop_1.lineTo(-0.22712, 0.31332)
loop_1 = loop_1.threePointArc((-0.28692, 0.31289), (-0.34828, 0.31407))
loop_1 = loop_1.threePointArc((-0.38579, 0.31338), (-0.42395, 0.31379))
loop_1 = loop_1.lineTo(0.8403, 0.32168)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/greedy_removal_iter12_test0_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/greedy_removal_iter12_test0_extrude.stl')