import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.30474, -0.19707, -0.19242), normal=(-0.03495, 0.73931, 0.67246), xDir=(0.99888, 0.04722, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.46482, 0.04048)
loop_1 = loop_1.lineTo(-0.45177, 0.04048)
loop_1 = loop_1.threePointArc((-0.43243, 0.0396), (-0.42262, 0.03888))
loop_1 = loop_1.lineTo(-0.41466, 0.01853)
loop_1 = loop_1.lineTo(-0.3983, 0.01115)
loop_1 = loop_1.threePointArc((-0.39006, 0.00426), (-0.38223, -0.00168))
loop_1 = loop_1.lineTo(-0.36971, -0.01363)
loop_1 = loop_1.lineTo(-0.38318, -0.01706)
loop_1 = loop_1.threePointArc((-0.39516, -0.01902), (-0.40666, -0.02093))
loop_1 = loop_1.threePointArc((-0.42611, -0.02543), (-0.43731, -0.028))
loop_1 = loop_1.lineTo(-0.45469, -0.02579)
loop_1 = loop_1.threePointArc((-0.4641, -0.01591), (-0.47314, -0.00642))
loop_1 = loop_1.lineTo(-0.46691, 0.02131)
loop_1 = loop_1.threePointArc((-0.46575, 0.03096), (-0.46497, 0.03886))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_6_interval_0.stl')