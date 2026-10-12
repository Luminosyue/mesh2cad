import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00445, 0.01981)
loop_1 = loop_1.lineTo(-0.01884, 0.01216)
loop_1 = loop_1.lineTo(-0.01877, -0.01227)
loop_1 = loop_1.lineTo(0.0045, -0.01975)
loop_1 = loop_1.lineTo(0.01879, 7e-05)
loop_1 = loop_1.lineTo(0.00447, 0.01978)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0076_00761963/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0076_00761963/sketch_7_interval_0.stl')