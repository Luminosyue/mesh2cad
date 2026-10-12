import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04202, 0.26304, 0.6002), normal=(-3e-05, -0.69093, 0.72292), xDir=(-1.0, 5e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12084, -0.06623)
loop_1 = loop_1.lineTo(0.37863, 0.03075)
loop_1 = loop_1.lineTo(0.39595, 0.02844)
loop_1 = loop_1.lineTo(0.41323, 0.01633)
loop_1 = loop_1.lineTo(0.42851, -0.00106)
loop_1 = loop_1.lineTo(0.43851, -0.02047)
loop_1 = loop_1.lineTo(0.44297, -0.03253)
loop_1 = loop_1.lineTo(0.44503, -0.0436)
loop_1 = loop_1.lineTo(0.45804, -0.07288)
loop_1 = loop_1.lineTo(0.08574, -0.07289)
loop_1 = loop_1.lineTo(0.10449, -0.07017)
loop_1 = loop_1.lineTo(0.11675, -0.06722)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_2_interval_0.stl')