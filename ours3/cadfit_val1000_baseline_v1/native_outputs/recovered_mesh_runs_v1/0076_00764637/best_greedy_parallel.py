import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02078, -1.0, 0.04309), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2973, 0.15309)
loop_1 = loop_1.lineTo(-0.26991, 0.15309)
loop_1 = loop_1.lineTo(-0.26991, -0.03952)
loop_1 = loop_1.lineTo(0.22835, -0.03952)
loop_1 = loop_1.lineTo(0.22878, 0.15309)
loop_1 = loop_1.lineTo(0.25574, 0.15309)
loop_1 = loop_1.lineTo(0.25574, -0.06691)
loop_1 = loop_1.lineTo(-0.2973, -0.06691)
loop_1 = loop_1.lineTo(-0.2973, 0.15103)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0076_00764637/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0076_00764637/sketch_10_interval_0.stl')