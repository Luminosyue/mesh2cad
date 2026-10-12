import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04689, -0.28429, -0.104), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.04689, 0.61028)
loop_1 = loop_1.lineTo(-1.04689, -0.24686)
loop_1 = loop_1.lineTo(-0.47546, -0.24686)
loop_1 = loop_1.lineTo(-0.47546, -0.81829)
loop_1 = loop_1.lineTo(0.38168, -0.81829)
loop_1 = loop_1.lineTo(0.95311, -0.24686)
loop_1 = loop_1.lineTo(0.95311, 0.61028)
loop_1 = loop_1.lineTo(-1.0143, 0.61028)
loop_1 = loop_1.lineTo(-1.04689, 0.61028)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0031_00317672/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0031_00317672/sketch_1_interval_0.stl')