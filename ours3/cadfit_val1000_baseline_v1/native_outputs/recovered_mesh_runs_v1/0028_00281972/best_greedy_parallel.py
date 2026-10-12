import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01807, 1.0, -0.09653), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98193, 0.90347)
loop_1 = loop_1.lineTo(0.98193, -1.09653)
loop_1 = loop_1.lineTo(0.31526, -1.09653)
loop_1 = loop_1.lineTo(0.31526, -0.09653)
loop_1 = loop_1.lineTo(-0.35141, -0.09653)
loop_1 = loop_1.lineTo(-0.35141, -1.09653)
loop_1 = loop_1.lineTo(-1.01807, -1.09653)
loop_1 = loop_1.lineTo(-1.01807, 0.90347)
loop_1 = loop_1.lineTo(0.97255, 0.90347)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0028_00281972/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0028_00281972/sketch_7_interval_0.stl')