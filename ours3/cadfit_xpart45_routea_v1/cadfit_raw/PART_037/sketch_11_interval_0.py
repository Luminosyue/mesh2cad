import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.09482, -0.00601, 0.21624), normal=(-0.00112, -0.82059, -0.57152), xDir=(-1.0, 0.00137, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.50167, 0.33214)
loop_1 = loop_1.threePointArc((-0.49471, 0.33178), (-0.48803, 0.33149))
loop_1 = loop_1.lineTo(-0.46742, 0.31098)
loop_1 = loop_1.threePointArc((-0.46511, 0.30298), (-0.46305, 0.29455))
loop_1 = loop_1.lineTo(-0.46038, 0.27689)
loop_1 = loop_1.lineTo(-0.45887, 0.26284)
loop_1 = loop_1.lineTo(-0.46046, 0.24578)
loop_1 = loop_1.lineTo(-0.46779, 0.22959)
loop_1 = loop_1.lineTo(-0.50461, 0.17628)
loop_1 = loop_1.lineTo(-0.51583, 0.17924)
loop_1 = loop_1.lineTo(-0.53665, 0.26523)
loop_1 = loop_1.lineTo(-0.50167, 0.33214)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_11_interval_0.stl')