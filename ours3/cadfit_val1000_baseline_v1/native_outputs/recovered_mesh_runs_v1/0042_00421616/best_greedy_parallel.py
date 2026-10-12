import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.13783, 0.03233, -0.83667), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.699, 0.86217)
loop_1 = loop_1.lineTo(-0.699, 0.1955)
loop_1 = loop_1.lineTo(-0.36566, 0.1955)
loop_1 = loop_1.lineTo(-0.36566, -1.13783)
loop_1 = loop_1.lineTo(0.301, -1.13783)
loop_1 = loop_1.lineTo(0.301, 0.1955)
loop_1 = loop_1.lineTo(0.63434, 0.1955)
loop_1 = loop_1.lineTo(0.63434, 0.86217)
loop_1 = loop_1.lineTo(-0.69733, 0.86217)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00421616/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00421616/sketch_1_interval_0.stl')