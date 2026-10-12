import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.11865, 0.04091, -0.12144), normal=(0.37744, 0.41471, 0.82798), xDir=(0.73955, -0.6731, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32233, 0.06021)
loop_1 = loop_1.lineTo(0.31925, 0.05002)
loop_1 = loop_1.lineTo(0.31788, 0.03043)
loop_1 = loop_1.lineTo(0.31316, 0.00786)
loop_1 = loop_1.lineTo(0.30828, -0.00607)
loop_1 = loop_1.lineTo(0.30941, -0.02557)
loop_1 = loop_1.lineTo(0.30185, -0.06466)
loop_1 = loop_1.lineTo(0.30249, -0.075)
loop_1 = loop_1.lineTo(0.29512, -0.10074)
loop_1 = loop_1.threePointArc((0.30136, -0.10265), (0.30718, -0.10265))
loop_1 = loop_1.lineTo(0.309, -0.07753)
loop_1 = loop_1.lineTo(0.31285, -0.03862)
loop_1 = loop_1.threePointArc((0.31817, 0.00439), (0.32249, 0.04285))
loop_1 = loop_1.lineTo(0.32603, 0.07361)
loop_1 = loop_1.lineTo(0.3272, 0.09103)
loop_1 = loop_1.lineTo(0.32233, 0.06021)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_17_interval_0.stl')