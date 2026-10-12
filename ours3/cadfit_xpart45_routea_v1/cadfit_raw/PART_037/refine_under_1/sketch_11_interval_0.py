import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07884, 0.01134, -0.16461), normal=(-0.00026, -0.01951, 0.99981), xDir=(-0.0, 0.99981, 0.01951))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03229, -0.50049)
loop_1 = loop_1.lineTo(0.00876, -0.52245)
loop_1 = loop_1.threePointArc((0.01615, -0.52112), (0.02219, -0.51991))
loop_1 = loop_1.lineTo(0.03593, -0.51326)
loop_1 = loop_1.threePointArc((0.04132, -0.50741), (0.04605, -0.50163))
loop_1 = loop_1.lineTo(0.04358, -0.48475)
loop_1 = loop_1.lineTo(0.03574, -0.47219)
loop_1 = loop_1.lineTo(0.02191, -0.46088)
loop_1 = loop_1.lineTo(-0.00637, -0.4435)
loop_1 = loop_1.lineTo(-0.01962, -0.44164)
loop_1 = loop_1.lineTo(-0.03229, -0.50049)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_11_interval_0.stl')