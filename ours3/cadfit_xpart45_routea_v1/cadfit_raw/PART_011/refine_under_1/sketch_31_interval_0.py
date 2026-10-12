import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.28684, 0.8215, 0.00923), normal=(0.51752, -0.85527, -0.02629), xDir=(-0.85556, -0.5177, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34058, 0.08724)
loop_1 = loop_1.lineTo(-0.35181, -0.15109)
loop_1 = loop_1.lineTo(-0.35208, -0.13661)
loop_1 = loop_1.lineTo(-0.36196, -0.09625)
loop_1 = loop_1.lineTo(-0.36355, -0.0861)
loop_1 = loop_1.lineTo(-0.36271, -0.04025)
loop_1 = loop_1.threePointArc((-0.35438, 0.00374), (-0.34701, 0.0437))
loop_1 = loop_1.lineTo(-0.34439, 0.05587)
loop_1 = loop_1.threePointArc((-0.34266, 0.07142), (-0.34087, 0.08509))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_31_interval_0.stl')