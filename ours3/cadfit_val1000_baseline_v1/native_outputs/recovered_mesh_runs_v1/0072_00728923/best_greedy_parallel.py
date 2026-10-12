import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.1635, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.61165, 0.61529)
loop_1 = loop_1.threePointArc((-0.90109, 0.4855), (-0.99873, 0.1963))
loop_1 = loop_1.lineTo(-0.9984, -0.25763)
loop_1 = loop_1.threePointArc((-0.8579, -0.52695), (-0.58084, -0.61429))
loop_1 = loop_1.lineTo(0.65224, -0.61341)
loop_1 = loop_1.threePointArc((0.91454, -0.46959), (0.99875, -0.1963))
loop_1 = loop_1.lineTo(0.9984, 0.25763)
loop_1 = loop_1.threePointArc((0.8579, 0.52695), (0.58084, 0.61429))
loop_1 = loop_1.lineTo(-0.60972, 0.61553)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.65049, 0.0)
loop_2 = loop_2.circle(0.15336)
loop_3 = sketch_1.moveTo(-0.65049, 0.0)
loop_3 = loop_3.circle(0.15336)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0072_00728923/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0072_00728923/sketch_3_interval_0.stl')