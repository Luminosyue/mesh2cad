import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.49, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.27734, 1.0)
loop_1 = loop_1.lineTo(0.14033, 0.90014)
loop_1 = loop_1.lineTo(0.02558, 0.78976)
loop_1 = loop_1.lineTo(-0.07319, 0.66488)
loop_1 = loop_1.lineTo(-0.15418, 0.5278)
loop_1 = loop_1.lineTo(-0.21589, 0.38103)
loop_1 = loop_1.lineTo(-0.2572, 0.22727)
loop_1 = loop_1.lineTo(-0.27734, 0.06933)
loop_1 = loop_1.lineTo(-0.27594, -0.08988)
loop_1 = loop_1.lineTo(-0.25304, -0.24744)
loop_1 = loop_1.lineTo(-0.20904, -0.40046)
loop_1 = loop_1.lineTo(-0.14477, -0.54613)
loop_1 = loop_1.lineTo(-0.06139, -0.68177)
loop_1 = loop_1.lineTo(0.03956, -0.80489)
loop_1 = loop_1.lineTo(0.15623, -0.91324)
loop_1 = loop_1.lineTo(0.27734, -0.99854)
loop_1 = loop_1.lineTo(0.27734, 0.99854)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.98)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0043_00435673/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0043_00435673/sketch_2_interval_0.stl')