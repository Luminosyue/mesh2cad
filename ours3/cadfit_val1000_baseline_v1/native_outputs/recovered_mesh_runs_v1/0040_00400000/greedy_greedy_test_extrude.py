import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.33315), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17872, 1.0)
loop_1 = loop_1.lineTo(-0.17738, 0.35035)
loop_1 = loop_1.lineTo(0.17872, 0.35169)
loop_1 = loop_1.lineTo(0.17738, 1.0)
loop_1 = loop_1.lineTo(-0.17805, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

plane_2 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.17872, 0.33315)
loop_1 = loop_1.lineTo(-0.17872, 0.33205)
loop_1 = loop_1.lineTo(-0.17761, -0.13824)
loop_1 = loop_1.lineTo(0.17872, -0.13714)
loop_1 = loop_1.lineTo(0.17872, 0.3326)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.65)

result = solid_1
result = result.add(solid_2)
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0040_00400000/greedy_greedy_test_extrude.stl')
print(f'Successfully exported 2 solids to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0040_00400000/greedy_greedy_test_extrude.stl')