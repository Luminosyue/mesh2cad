import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03733, -0.00411, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99589, 0.46267)
loop_1 = loop_1.lineTo(-0.99589, -1.03733)
loop_1 = loop_1.lineTo(-0.49589, -1.03733)
loop_1 = loop_1.lineTo(-0.49589, -0.28733)
loop_1 = loop_1.lineTo(0.50411, -0.28733)
loop_1 = loop_1.lineTo(0.50411, -1.03733)
loop_1 = loop_1.lineTo(1.00411, -1.03733)
loop_1 = loop_1.lineTo(1.00411, 0.46267)
loop_1 = loop_1.lineTo(0.50411, 0.46267)
loop_1 = loop_1.lineTo(0.50411, 0.96267)
loop_1 = loop_1.lineTo(-0.49589, 0.96267)
loop_1 = loop_1.lineTo(-0.49589, 0.46267)
loop_1 = loop_1.lineTo(-0.94714, 0.46267)
loop_1 = loop_1.lineTo(-0.99589, 0.46267)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0013_00130675/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0013_00130675/sketch_0_interval_0.stl')