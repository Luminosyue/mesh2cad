import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.42939, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33939, -0.53042)
loop_1 = loop_1.lineTo(0.33888, -0.78867)
loop_1 = loop_1.lineTo(0.32971, -0.76331)
loop_1 = loop_1.lineTo(0.31897, -0.72706)
loop_1 = loop_1.lineTo(0.31652, -0.7134)
loop_1 = loop_1.lineTo(0.31495, -0.69874)
loop_1 = loop_1.threePointArc((0.31796, -0.67185), (0.32249, -0.6517))
loop_1 = loop_1.threePointArc((0.32767, -0.63346), (0.33227, -0.61603))
loop_1 = loop_1.threePointArc((0.33342, -0.60835), (0.33441, -0.60114))
loop_1 = loop_1.threePointArc((0.33626, -0.58227), (0.33773, -0.5643))
loop_1 = loop_1.lineTo(0.33801, -0.54212)
loop_1 = loop_1.lineTo(0.33937, -0.53059)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_71_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_71_interval_0.stl')