import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.34361, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.63387, -0.43068)
loop_1 = loop_1.lineTo(0.51334, -0.41649)
loop_1 = loop_1.lineTo(0.52527, -0.41413)
loop_1 = loop_1.threePointArc((0.53218, -0.41247), (0.53928, -0.41089))
loop_1 = loop_1.lineTo(0.56963, -0.4047)
loop_1 = loop_1.lineTo(0.57971, -0.40421)
loop_1 = loop_1.threePointArc((0.58583, -0.40389), (0.59169, -0.40331))
loop_1 = loop_1.lineTo(0.60201, -0.40229)
loop_1 = loop_1.lineTo(0.61654, -0.40032)
loop_1 = loop_1.lineTo(0.63164, -0.42387)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.59)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_74_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_74_interval_0.stl')