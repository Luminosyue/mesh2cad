import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47724, 0.0711, 0.03495), normal=(0.01988, -0.75052, -0.66054), xDir=(-0.99965, -0.02649, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.64344, 0.07552)
loop_1 = loop_1.threePointArc((0.63556, 0.0742), (0.62734, 0.07283))
loop_1 = loop_1.threePointArc((0.61909, 0.06572), (0.61105, 0.05887))
loop_1 = loop_1.lineTo(0.6038, 0.03225)
loop_1 = loop_1.lineTo(0.64421, 0.03222)
loop_1 = loop_1.lineTo(0.64371, 0.05572)
loop_1 = loop_1.lineTo(0.64344, 0.07551)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_10_interval_0.stl')