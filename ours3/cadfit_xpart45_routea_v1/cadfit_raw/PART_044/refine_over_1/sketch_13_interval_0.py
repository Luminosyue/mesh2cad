import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57748, 0.07717, -0.05643), normal=(0.16174, -0.98683, -3e-05), xDir=(-0.98683, -0.16174, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13309, 0.78357)
loop_1 = loop_1.lineTo(0.08998, 0.78356)
loop_1 = loop_1.lineTo(0.09149, 0.76181)
loop_1 = loop_1.lineTo(0.09363, 0.72338)
loop_1 = loop_1.lineTo(0.09643, 0.70806)
loop_1 = loop_1.threePointArc((0.09931, 0.68516), (0.10212, 0.66419))
loop_1 = loop_1.lineTo(0.10649, 0.63285)
loop_1 = loop_1.lineTo(0.10786, 0.61695)
loop_1 = loop_1.lineTo(0.11157, 0.58906)
loop_1 = loop_1.threePointArc((0.11466, 0.56493), (0.11709, 0.54387))
loop_1 = loop_1.lineTo(0.12162, 0.51932)
loop_1 = loop_1.threePointArc((0.12464, 0.50491), (0.12699, 0.49353))
loop_1 = loop_1.lineTo(0.12949, 0.47766)
loop_1 = loop_1.lineTo(0.13122, 0.46647)
loop_1 = loop_1.lineTo(0.13255, 0.45522)
loop_1 = loop_1.lineTo(0.13309, 0.77995)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_13_interval_0.stl')