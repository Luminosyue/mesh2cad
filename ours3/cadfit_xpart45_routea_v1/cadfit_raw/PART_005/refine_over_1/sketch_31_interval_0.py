import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05572, -0.0488, -0.51982), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16089, -0.90487)
loop_1 = loop_1.lineTo(0.04645, -0.91888)
loop_1 = loop_1.lineTo(0.03074, -0.91897)
loop_1 = loop_1.lineTo(0.00795, -0.91848)
loop_1 = loop_1.lineTo(-0.4312, -0.91848)
loop_1 = loop_1.lineTo(-0.4312, -0.81223)
loop_1 = loop_1.lineTo(-0.37293, -0.83876)
loop_1 = loop_1.lineTo(-0.32135, -0.85919)
loop_1 = loop_1.lineTo(-0.27447, -0.87628)
loop_1 = loop_1.lineTo(-0.22264, -0.89316)
loop_1 = loop_1.lineTo(-0.17081, -0.90353)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_31_interval_0.stl')