import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.66667, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.83333)
loop_1 = loop_1.lineTo(-0.99512, -0.83333)
loop_1 = loop_1.lineTo(-0.33333, -0.83089)
loop_1 = loop_1.lineTo(-0.33089, 0.16667)
loop_1 = loop_1.lineTo(1.0, 0.17155)
loop_1 = loop_1.lineTo(0.99756, 0.83333)
loop_1 = loop_1.lineTo(-0.99756, 0.83333)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0073_00735801/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0073_00735801/sketch_0_interval_0.stl')