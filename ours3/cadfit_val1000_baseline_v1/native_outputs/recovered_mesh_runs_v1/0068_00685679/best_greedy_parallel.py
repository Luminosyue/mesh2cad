import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01192, 1.0, -0.15778), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98808, 0.50889)
loop_1 = loop_1.lineTo(-1.01192, 0.50889)
loop_1 = loop_1.lineTo(-1.01192, -0.15778)
loop_1 = loop_1.lineTo(-0.34525, -0.15778)
loop_1 = loop_1.lineTo(-0.34525, -0.82444)
loop_1 = loop_1.lineTo(0.32142, -0.82444)
loop_1 = loop_1.lineTo(0.32142, -0.15778)
loop_1 = loop_1.lineTo(0.98808, -0.15778)
loop_1 = loop_1.lineTo(0.98808, 0.50472)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0068_00685679/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0068_00685679/sketch_3_interval_0.stl')