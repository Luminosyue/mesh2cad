import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14272, 0.24776)
loop_1 = loop_1.lineTo(-0.11401, 0.32972)
loop_1 = loop_1.lineTo(-0.09516, 0.32308)
loop_1 = loop_1.lineTo(-0.1245, 0.23912)
loop_1 = loop_1.lineTo(-0.11317, 0.23769)
loop_1 = loop_1.lineTo(-0.09104, 0.24437)
loop_1 = loop_1.lineTo(-0.07578, 0.26087)
loop_1 = loop_1.threePointArc((-0.07334, 0.26785), (-0.07075, 0.2751))
loop_1 = loop_1.lineTo(-0.08159, 0.31642)
loop_1 = loop_1.lineTo(-0.14272, 0.24776)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_19_interval_0.stl')