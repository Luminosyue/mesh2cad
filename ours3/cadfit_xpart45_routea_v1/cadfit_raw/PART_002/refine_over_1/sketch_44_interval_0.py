import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.55206, -0.08469, -0.04717), normal=(0.99998, -0.00591, -0.00178), xDir=(-0.00591, -0.99998, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11124, -0.29721)
loop_1 = loop_1.lineTo(-0.16348, -0.31668)
loop_1 = loop_1.lineTo(-0.16255, -0.54853)
loop_1 = loop_1.lineTo(-0.15694, -0.53031)
loop_1 = loop_1.lineTo(-0.15464, -0.51873)
loop_1 = loop_1.lineTo(-0.14538, -0.49143)
loop_1 = loop_1.threePointArc((-0.1399, -0.48001), (-0.13621, -0.47255))
loop_1 = loop_1.threePointArc((-0.12384, -0.43683), (-0.1131, -0.40514))
loop_1 = loop_1.lineTo(-0.10836, -0.39237)
loop_1 = loop_1.lineTo(-0.09936, -0.37068)
loop_1 = loop_1.lineTo(-0.09878, -0.35833)
loop_1 = loop_1.lineTo(-0.09907, -0.33367)
loop_1 = loop_1.lineTo(-0.1082, -0.29649)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_44_interval_0.stl')