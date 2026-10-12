import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14973, 0.54003)
loop_1 = loop_1.lineTo(0.1529, 0.52979)
loop_1 = loop_1.threePointArc((0.16073, 0.51575), (0.16552, 0.50846))
loop_1 = loop_1.lineTo(0.22218, 0.51034)
loop_1 = loop_1.threePointArc((0.22573, 0.51764), (0.22955, 0.52519))
loop_1 = loop_1.lineTo(0.23388, 0.55983)
loop_1 = loop_1.threePointArc((0.23144, 0.56737), (0.22906, 0.5746))
loop_1 = loop_1.lineTo(0.18499, 0.59418)
loop_1 = loop_1.lineTo(0.17294, 0.59105)
loop_1 = loop_1.threePointArc((0.16186, 0.58291), (0.15497, 0.57673))
loop_1 = loop_1.lineTo(0.14973, 0.54003)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_23_interval_0.stl')