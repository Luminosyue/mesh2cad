import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0007, -1.0, 0.00024), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16324, 0.16417)
loop_1 = loop_1.lineTo(0.16463, 0.16417)
loop_1 = loop_1.lineTo(0.16463, -0.16369)
loop_1 = loop_1.lineTo(-0.16324, -0.16369)
loop_1 = loop_1.lineTo(-0.16324, 0.15598)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.13045, 0.13139)
loop_2 = loop_2.lineTo(-0.13045, -0.13091)
loop_2 = loop_2.lineTo(0.13185, -0.13091)
loop_2 = loop_2.lineTo(0.13185, 0.13139)
loop_2 = loop_2.lineTo(-0.12523, 0.13139)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0019_00191091/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0019_00191091/sketch_7_interval_0.stl')