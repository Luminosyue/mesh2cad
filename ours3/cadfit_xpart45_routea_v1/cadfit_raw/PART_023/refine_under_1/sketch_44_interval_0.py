import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49515, 0.44978, 0.03134), normal=(0.00466, -0.99999, 1e-05), xDir=(-0.99999, -0.00466, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04856, -0.57694)
loop_1 = loop_1.lineTo(0.01897, -0.57892)
loop_1 = loop_1.lineTo(0.02344, -0.94492)
loop_1 = loop_1.threePointArc((0.03347, -0.9458), (0.04982, -0.94547))
loop_1 = loop_1.lineTo(0.05706, -0.57936)
loop_1 = loop_1.lineTo(0.06879, -0.5797)
loop_1 = loop_1.lineTo(0.0487, -0.57697)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_44_interval_0.stl')