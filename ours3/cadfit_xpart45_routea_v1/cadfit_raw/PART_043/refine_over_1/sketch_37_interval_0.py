import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50659, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.58485, 0.22064)
loop_1 = loop_1.lineTo(0.57123, 0.21254)
loop_1 = loop_1.lineTo(0.56386, 0.18585)
loop_1 = loop_1.threePointArc((0.56401, 0.09261), (0.56205, -0.00395))
loop_1 = loop_1.lineTo(0.56195, -0.40449)
loop_1 = loop_1.lineTo(0.5608, -0.45843)
loop_1 = loop_1.lineTo(0.56873, -0.44829)
loop_1 = loop_1.lineTo(0.57556, -0.43087)
loop_1 = loop_1.threePointArc((0.57639, -0.42445), (0.57631, -0.41873))
loop_1 = loop_1.threePointArc((0.57663, -0.39832), (0.57563, -0.37925))
loop_1 = loop_1.threePointArc((0.5753, -0.33149), (0.5735, -0.2862))
loop_1 = loop_1.lineTo(0.57224, -0.16203)
loop_1 = loop_1.lineTo(0.57175, -0.1095)
loop_1 = loop_1.lineTo(0.57211, 0.03056)
loop_1 = loop_1.threePointArc((0.57189, 0.01531), (0.57197, 0.00118))
loop_1 = loop_1.threePointArc((0.57207, 0.01851), (0.5726, 0.03602))
loop_1 = loop_1.lineTo(0.58481, 0.22013)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_37_interval_0.stl')