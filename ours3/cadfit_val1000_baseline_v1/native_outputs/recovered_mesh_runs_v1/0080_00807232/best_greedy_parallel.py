import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01458), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.04167)
loop_1 = loop_1.lineTo(-0.99861, -0.04167)
loop_1 = loop_1.lineTo(1.0, -0.03611)
loop_1 = loop_1.lineTo(0.99861, 0.04167)
loop_1 = loop_1.lineTo(-0.99861, 0.04167)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0080_00807232/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0080_00807232/sketch_5_interval_0.stl')