import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21769), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.63246, 0.56741)
loop_1 = loop_1.threePointArc((-0.62124, 0.5544), (-0.6099, 0.54056))
loop_1 = loop_1.threePointArc((-0.58682, 0.51128), (-0.56342, 0.48456))
loop_1 = loop_1.threePointArc((-0.53077, 0.44766), (-0.49862, 0.41336))
loop_1 = loop_1.threePointArc((-0.47606, 0.38704), (-0.45383, 0.36266))
loop_1 = loop_1.lineTo(-0.42547, 0.32843)
loop_1 = loop_1.threePointArc((-0.41663, 0.3187), (-0.40803, 0.30985))
loop_1 = loop_1.lineTo(-0.39786, 0.30055)
loop_1 = loop_1.threePointArc((-0.38726, 0.28925), (-0.37661, 0.27886))
loop_1 = loop_1.lineTo(-0.35867, 0.26689)
loop_1 = loop_1.lineTo(-0.3374, 0.26828)
loop_1 = loop_1.lineTo(-0.63218, 0.56727)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_56_interval_0.stl')