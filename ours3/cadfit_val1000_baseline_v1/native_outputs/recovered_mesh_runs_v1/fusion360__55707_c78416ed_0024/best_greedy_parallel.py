import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01928, 0.09941, 0.764), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49941, 0.98072)
loop_1 = loop_1.lineTo(0.49941, -1.01928)
loop_1 = loop_1.lineTo(0.19941, -1.01928)
loop_1 = loop_1.lineTo(0.19941, -0.41928)
loop_1 = loop_1.lineTo(-0.30059, -0.41928)
loop_1 = loop_1.lineTo(-0.30059, 0.38072)
loop_1 = loop_1.lineTo(0.19941, 0.38072)
loop_1 = loop_1.lineTo(0.19941, 0.98072)
loop_1 = loop_1.lineTo(0.46935, 0.98072)
loop_1 = loop_1.lineTo(0.49941, 0.98072)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__55707_c78416ed_0024/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__55707_c78416ed_0024/sketch_3_interval_0.stl')