import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.99171, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.59851, 0.33924)
loop_1 = loop_1.lineTo(-0.64754, 0.30658)
loop_1 = loop_1.lineTo(-0.64724, 0.11987)
loop_1 = loop_1.lineTo(-0.64398, 0.14958)
loop_1 = loop_1.lineTo(-0.63849, 0.18997)
loop_1 = loop_1.lineTo(-0.6324, 0.22695)
loop_1 = loop_1.lineTo(-0.62184, 0.26688)
loop_1 = loop_1.threePointArc((-0.6145, 0.28695), (-0.60664, 0.30759))
loop_1 = loop_1.lineTo(-0.59734, 0.32788)
loop_1 = loop_1.lineTo(-0.59849, 0.33908)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_50_interval_0.stl')