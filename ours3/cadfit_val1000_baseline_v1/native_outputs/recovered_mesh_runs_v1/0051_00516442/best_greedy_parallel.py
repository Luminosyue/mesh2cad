import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0319, -0.01718, 0.05), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.48282, 0.5931)
loop_1 = loop_1.lineTo(0.48282, -0.6569)
loop_1 = loop_1.lineTo(0.09532, -0.6569)
loop_1 = loop_1.lineTo(0.09532, -1.0319)
loop_1 = loop_1.lineTo(-0.12968, -1.0319)
loop_1 = loop_1.lineTo(-0.12968, -0.6569)
loop_1 = loop_1.lineTo(-0.51718, -0.6569)
loop_1 = loop_1.lineTo(-0.51718, 0.5931)
loop_1 = loop_1.lineTo(-0.12968, 0.5931)
loop_1 = loop_1.lineTo(-0.12968, 0.9681)
loop_1 = loop_1.lineTo(0.09532, 0.9681)
loop_1 = loop_1.lineTo(0.09532, 0.5931)
loop_1 = loop_1.lineTo(0.47071, 0.5931)
loop_1 = loop_1.lineTo(0.48282, 0.5931)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.01718, -0.0319)
loop_2 = loop_2.circle(0.08638)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0051_00516442/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0051_00516442/sketch_1_interval_0.stl')