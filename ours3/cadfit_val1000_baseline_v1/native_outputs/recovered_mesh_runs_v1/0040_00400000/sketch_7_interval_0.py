import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.18, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.33315)
loop_1 = loop_1.lineTo(-0.35035, 0.33166)
loop_1 = loop_1.lineTo(-0.35184, -0.13824)
loop_1 = loop_1.lineTo(-1.0, -0.13674)
loop_1 = loop_1.lineTo(-1.0, 0.3324)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0040_00400000/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0040_00400000/sketch_7_interval_0.stl')