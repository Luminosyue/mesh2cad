import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35869, 0.2582, 0.04106), normal=(-0.00567, 0.87903, 0.47673), xDir=(0.99998, 0.00645, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.25839, 0.71069)
loop_1 = loop_1.lineTo(0.59671, 0.15271)
loop_1 = loop_1.threePointArc((0.58522, 0.17583), (0.57541, 0.19318))
loop_1 = loop_1.lineTo(1.25838, 0.71068)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_23_interval_0.stl')