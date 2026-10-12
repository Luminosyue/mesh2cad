import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19358, 0.66333, -0.24804), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.19358, 0.75196)
loop_1 = loop_1.lineTo(1.19358, 0.0853)
loop_1 = loop_1.lineTo(0.52691, 0.0853)
loop_1 = loop_1.lineTo(0.52691, -0.58137)
loop_1 = loop_1.lineTo(-0.13976, -0.58137)
loop_1 = loop_1.lineTo(-0.13976, -1.24804)
loop_1 = loop_1.lineTo(-0.80642, -1.24804)
loop_1 = loop_1.lineTo(-0.80642, 0.75196)
loop_1 = loop_1.lineTo(1.18733, 0.75196)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0028_00281977/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0028_00281977/sketch_9_interval_0.stl')