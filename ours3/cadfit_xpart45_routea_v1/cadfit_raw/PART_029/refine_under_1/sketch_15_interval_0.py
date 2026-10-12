import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.59751, -0.02609, -0.22), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13515, 1.56916)
loop_1 = loop_1.lineTo(0.13515, 1.36971)
loop_1 = loop_1.lineTo(0.1456, 1.36977)
loop_1 = loop_1.lineTo(0.15515, 1.44169)
loop_1 = loop_1.lineTo(0.15515, 1.45692)
loop_1 = loop_1.threePointArc((0.15515, 1.46831), (0.15515, 1.48018))
loop_1 = loop_1.lineTo(0.15515, 1.5066)
loop_1 = loop_1.lineTo(0.15515, 1.56168)
loop_1 = loop_1.lineTo(0.13515, 1.56916)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_15_interval_0.stl')