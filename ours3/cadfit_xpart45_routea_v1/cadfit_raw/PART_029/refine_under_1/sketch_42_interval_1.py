import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05234, 0.04365)
loop_1 = loop_1.lineTo(0.04171, 0.03109)
loop_1 = loop_1.lineTo(-0.07004, -0.10049)
loop_1 = loop_1.lineTo(-0.08575, -0.11762)
loop_1 = loop_1.lineTo(-0.09376, -0.1305)
loop_1 = loop_1.lineTo(-0.08657, -0.12034)
loop_1 = loop_1.lineTo(-0.03684, -0.14531)
loop_1 = loop_1.threePointArc((-0.02928, -0.14109), (-0.02248, -0.13793))
loop_1 = loop_1.lineTo(0.11079, -0.1397)
loop_1 = loop_1.lineTo(0.11053, -0.02814)
loop_1 = loop_1.lineTo(0.00733, -0.06917)
loop_1 = loop_1.lineTo(0.04268, 0.00161)
loop_1 = loop_1.lineTo(0.05719, 0.02899)
loop_1 = loop_1.lineTo(0.08623, 0.02367)
loop_1 = loop_1.threePointArc((0.08097, 0.02792), (0.07586, 0.03154))
loop_1 = loop_1.threePointArc((0.06894, 0.03586), (0.0624, 0.03963))
loop_1 = loop_1.threePointArc((0.05717, 0.04181), (0.05234, 0.04364))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_42_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_42_interval_1.stl')