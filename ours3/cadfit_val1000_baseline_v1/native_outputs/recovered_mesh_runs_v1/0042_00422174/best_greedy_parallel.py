import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00582, -0.2, -0.07676), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14418, 0.92324)
loop_1 = loop_1.lineTo(-0.14418, -1.07676)
loop_1 = loop_1.lineTo(0.15582, -1.07676)
loop_1 = loop_1.lineTo(0.15582, -0.67676)
loop_1 = loop_1.lineTo(-0.01737, -0.67676)
loop_1 = loop_1.lineTo(-0.01737, -0.26801)
loop_1 = loop_1.lineTo(0.15582, -0.26801)
loop_1 = loop_1.lineTo(0.15582, 0.92324)
loop_1 = loop_1.lineTo(-0.13949, 0.92324)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00422174/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00422174/sketch_5_interval_0.stl')