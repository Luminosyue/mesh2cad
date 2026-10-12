import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16348, 0.11547)
loop_1 = loop_1.threePointArc((-0.15582, 0.11889), (-0.14778, 0.12228))
loop_1 = loop_1.lineTo(-0.12683, 0.15945)
loop_1 = loop_1.threePointArc((-0.12796, 0.1672), (-0.12909, 0.17528))
loop_1 = loop_1.threePointArc((-0.13996, 0.18614), (-0.14224, 0.18856))
loop_1 = loop_1.lineTo(-0.16723, 0.11706)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_20_interval_0.stl')