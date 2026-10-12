import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.15886, -0.13268, -0.04908), normal=(0.69558, -0.71845, -6e-05), xDir=(-0.71845, -0.69558, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07653, 0.24456)
loop_1 = loop_1.lineTo(0.07654, 0.22969)
loop_1 = loop_1.lineTo(0.10816, 0.22642)
loop_1 = loop_1.lineTo(0.12464, 0.22438)
loop_1 = loop_1.threePointArc((0.13384, 0.22385), (0.14152, 0.22363))
loop_1 = loop_1.lineTo(0.17409, 0.2227)
loop_1 = loop_1.lineTo(0.18796, 0.2229)
loop_1 = loop_1.lineTo(0.16578, 0.23068)
loop_1 = loop_1.lineTo(0.15354, 0.23432)
loop_1 = loop_1.lineTo(0.14195, 0.23738)
loop_1 = loop_1.lineTo(0.11899, 0.23925)
loop_1 = loop_1.lineTo(0.09719, 0.24167)
loop_1 = loop_1.lineTo(0.07689, 0.2445)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_11_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_11_interval_1.stl')