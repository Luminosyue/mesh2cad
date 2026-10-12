import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.19), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.6661, 1.0)
loop_1 = loop_1.lineTo(-0.66164, -0.14041)
loop_1 = loop_1.lineTo(-0.30993, -0.14264)
loop_1 = loop_1.lineTo(-0.30771, -1.0)
loop_1 = loop_1.lineTo(0.6661, -0.99555)
loop_1 = loop_1.lineTo(0.66166, 0.29795)
loop_1 = loop_1.lineTo(-0.17637, 0.30017)
loop_1 = loop_1.lineTo(-0.1786, 1.0)
loop_1 = loop_1.lineTo(-0.66387, 1.0)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.375, -0.15069)
loop_2 = loop_2.circle(0.1144)
loop_3 = sketch_1.moveTo(0.54966, 0.09589)
loop_3 = loop_3.circle(0.09687)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0037_00377111/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0037_00377111/sketch_2_interval_0.stl')