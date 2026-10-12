import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.20692, 0.67333, -0.21456), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.20692, 0.78544)
loop_1 = loop_1.lineTo(1.20692, 0.11877)
loop_1 = loop_1.lineTo(0.54025, 0.11877)
loop_1 = loop_1.lineTo(0.54025, -0.54789)
loop_1 = loop_1.lineTo(-0.12642, -0.54789)
loop_1 = loop_1.lineTo(-0.12642, -1.21456)
loop_1 = loop_1.lineTo(-0.79308, -1.21456)
loop_1 = loop_1.lineTo(-0.79308, 0.78544)
loop_1 = loop_1.lineTo(1.20067, 0.78544)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00422426/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00422426/sketch_6_interval_0.stl')