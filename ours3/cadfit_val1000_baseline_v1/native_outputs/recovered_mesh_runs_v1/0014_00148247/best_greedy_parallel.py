import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.09319, 0.48793, 0.71156), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.48793, 0.53763)
loop_1 = loop_1.lineTo(1.48793, -0.35125)
loop_1 = loop_1.lineTo(-0.51207, -0.35125)
loop_1 = loop_1.lineTo(-0.51207, 0.53763)
loop_1 = loop_1.lineTo(1.45264, 0.53763)
loop_1 = loop_1.lineTo(1.48793, 0.53763)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(1.15459, 0.09319)
loop_2 = loop_2.circle(0.14883)
loop_3 = sketch_1.moveTo(-0.17874, 0.09319)
loop_3 = loop_3.circle(0.14883)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(1.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0014_00148247/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0014_00148247/sketch_1_interval_0.stl')