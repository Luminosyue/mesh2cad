import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.56008, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80939, 0.15479)
loop_1 = loop_1.lineTo(0.8085, -0.16677)
loop_1 = loop_1.lineTo(0.78134, -0.16646)
loop_1 = loop_1.lineTo(0.79614, -0.15208)
loop_1 = loop_1.threePointArc((0.80135, -0.1267), (0.80564, -0.10239))
loop_1 = loop_1.lineTo(0.8062, -0.06583)
loop_1 = loop_1.threePointArc((0.80607, -0.05496), (0.80671, -0.04389))
loop_1 = loop_1.threePointArc((0.80777, -0.02334), (0.80835, -0.00382))
loop_1 = loop_1.lineTo(0.80803, 0.03394)
loop_1 = loop_1.threePointArc((0.80783, 0.04323), (0.80819, 0.05267))
loop_1 = loop_1.threePointArc((0.80869, 0.07318), (0.80877, 0.09264))
loop_1 = loop_1.threePointArc((0.80848, 0.11224), (0.80843, 0.13241))
loop_1 = loop_1.threePointArc((0.80882, 0.14338), (0.80943, 0.15456))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_29_interval_0.stl')