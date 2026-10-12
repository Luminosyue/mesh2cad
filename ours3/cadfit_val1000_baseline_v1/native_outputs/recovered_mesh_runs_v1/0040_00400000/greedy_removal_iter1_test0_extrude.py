import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17872, 0.33315)
loop_1 = loop_1.lineTo(-0.17872, 0.33205)
loop_1 = loop_1.lineTo(-0.17761, -0.13824)
loop_1 = loop_1.lineTo(0.17872, -0.13714)
loop_1 = loop_1.lineTo(0.17872, 0.3326)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0040_00400000/greedy_removal_iter1_test0_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0040_00400000/greedy_removal_iter1_test0_extrude.stl')