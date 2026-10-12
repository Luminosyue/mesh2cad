import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.43333, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.6)
loop_1 = loop_1.lineTo(-0.9957, -0.6)
loop_1 = loop_1.lineTo(-0.73333, -0.59787)
loop_1 = loop_1.lineTo(-0.72906, 0.46667)
loop_1 = loop_1.lineTo(1.0, 0.47083)
loop_1 = loop_1.lineTo(1.0, 0.6)
loop_1 = loop_1.lineTo(-0.99787, 0.6)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0078_00788299/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0078_00788299/sketch_3_interval_0.stl')