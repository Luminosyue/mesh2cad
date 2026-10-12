import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38699, -0.02201, -0.09603), normal=(0.99999, -0.00495, -0.00023), xDir=(-0.00495, -0.99999, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04184, 0.04589)
loop_1 = loop_1.lineTo(-0.0705, 0.04609)
loop_1 = loop_1.lineTo(-0.1333, 0.04653)
loop_1 = loop_1.lineTo(-0.20711, -0.00941)
loop_1 = loop_1.threePointArc((-0.19527, -0.01128), (-0.1935, -0.01214))
loop_1 = loop_1.threePointArc((-0.18395, -0.01306), (-0.18266, -0.01365))
loop_1 = loop_1.lineTo(-0.03331, -0.01866)
loop_1 = loop_1.lineTo(-0.03391, -0.00458)
loop_1 = loop_1.lineTo(-0.03361, 0.00696)
loop_1 = loop_1.lineTo(-0.03275, 0.02832)
loop_1 = loop_1.lineTo(-0.03155, 0.04653)
loop_1 = loop_1.lineTo(-0.04184, 0.04589)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_34_interval_0.stl')