import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.10367, -0.03556, -0.075), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.76444, 1.10367)
loop_1 = loop_1.lineTo(0.83556, 1.10367)
loop_1 = loop_1.lineTo(0.83556, -0.89633)
loop_1 = loop_1.lineTo(-0.76444, -0.89633)
loop_1 = loop_1.lineTo(-0.76444, 1.06795)
loop_1 = loop_1.lineTo(-0.76444, 1.10367)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

plane_2 = cq.Plane(origin=(-0.24753, 0.34433, 0.075), normal=(0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(1.14433, 0.75247)
loop_1 = loop_1.lineTo(-0.45567, 0.75247)
loop_1 = loop_1.lineTo(-0.45567, -1.24753)
loop_1 = loop_1.lineTo(1.14433, -1.24753)
loop_1 = loop_1.lineTo(1.14433, 0.71675)
loop_1 = loop_1.lineTo(1.14433, 0.75247)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.15)

result = solid_1
result = result.add(solid_2)
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0003_00037431/greedy_greedy_test_extrude.stl')
print(f'Successfully exported 2 solids to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0003_00037431/greedy_greedy_test_extrude.stl')