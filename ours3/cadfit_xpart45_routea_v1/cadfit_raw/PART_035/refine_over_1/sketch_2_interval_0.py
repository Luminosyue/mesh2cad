import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.92449, 0.30799, -0.03782), normal=(0.92728, -0.37435, 0.00299), xDir=(-0.37435, -0.92729, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1776, -0.27083)
loop_1 = loop_1.lineTo(-0.17533, 0.21442)
loop_1 = loop_1.lineTo(-0.11088, 0.21442)
loop_1 = loop_1.lineTo(-0.14333, -0.02925)
loop_1 = loop_1.lineTo(-0.16782, 0.00153)
loop_1 = loop_1.lineTo(-0.17085, 0.0244)
loop_1 = loop_1.lineTo(-0.17073, 0.05206)
loop_1 = loop_1.lineTo(-0.17156, 0.08156)
loop_1 = loop_1.lineTo(-0.1725, -0.0886)
loop_1 = loop_1.lineTo(-0.17651, -0.11362)
loop_1 = loop_1.threePointArc((-0.17602, -0.16254), (-0.17717, -0.20581))
loop_1 = loop_1.lineTo(-0.1767, -0.22831)
loop_1 = loop_1.lineTo(-0.17712, -0.25011)
loop_1 = loop_1.lineTo(-0.1731, -0.26683)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_2_interval_0.stl')