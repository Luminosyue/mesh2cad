import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00479, -0.04, 0.00225), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48479, 1.00225)
loop_1 = loop_1.lineTo(0.47521, 1.00225)
loop_1 = loop_1.lineTo(0.47521, -0.99775)
loop_1 = loop_1.lineTo(-0.48479, -0.99775)
loop_1 = loop_1.lineTo(-0.48479, 0.97248)
loop_1 = loop_1.lineTo(-0.48479, 1.00225)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.23521, -0.75775)
loop_2 = loop_2.circle(0.05529)
loop_3 = sketch_1.moveTo(0.23521, 0.76225)
loop_3 = loop_3.circle(0.05529)
loop_4 = sketch_1.moveTo(-0.24479, -0.75775)
loop_4 = loop_4.circle(0.05529)
loop_5 = sketch_1.moveTo(-0.24479, 0.76225)
loop_5 = loop_5.circle(0.05529)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3).add(loop_4).add(loop_5)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00896142/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00896142/sketch_1_interval_0.stl')