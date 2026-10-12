import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0105, 0.2739, 0.03), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.2739, 0.4895)
loop_1 = loop_1.lineTo(1.2739, -0.5105)
loop_1 = loop_1.lineTo(-0.7261, -0.5105)
loop_1 = loop_1.lineTo(-0.7261, 0.4895)
loop_1 = loop_1.lineTo(1.24414, 0.4895)
loop_1 = loop_1.lineTo(1.2739, 0.4895)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.5861, -0.0105)
loop_2 = loop_2.circle(0.07899)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0036_00364340/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0036_00364340/sketch_3_interval_0.stl')